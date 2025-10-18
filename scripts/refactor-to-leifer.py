#!/usr/bin/env python3
# refactor_to_leifer.py
# 2-space indentation per your preference

import argparse
import json
import os
import re
import shutil
from pathlib import Path

BONDOTO = "bondoto"
LEIFER = "leifer"

PY_EXTS = {".py"}
TEXT_EXTS = {".toml", ".md", ".sh", ".yml", ".yaml", ".cfg", ".ini", ".txt"}
CODE_EXTS = PY_EXTS | TEXT_EXTS

EXCLUDE_DIRS = {
  ".git", ".hg", ".svn", ".venv", "venv", "env", "dist", "build", "__pycache__",
  ".mypy_cache", ".pytest_cache", ".ruff_cache", ".idea", ".vscode", "node_modules"
}

RE_IMPORT_FROM = re.compile(rf"\bfrom {BONDOTO}(\b|\.)(.*)")
RE_IMPORT = re.compile(rf"\bimport {BONDOTO}(\b|\.)(.*)")


def replace_imports(text: str) -> tuple[str, int]:
  count = 0
  new = text
  new2, n1 = RE_IMPORT_FROM.subn(lambda m: f"from {LEIFER}{m.group(1)}{m.group(2)}",
                                 new)
  new = new2
  new2, n2 = RE_IMPORT.subn(lambda m: f"import {LEIFER}{m.group(1)}{m.group(2)}", new)
  count = n1 + n2
  return new2, count


def patch_pyproject(pyproj_path: Path) -> tuple[bool, dict]:
  if not pyproj_path.exists():
    return False, {}
  text = pyproj_path.read_text(encoding="utf-8")
  changed = False
  updates = {}

  # Project name
  name_re = re.compile(r'(?m)^\s*name\s*=\s*"([^"]+)"\s*$')

  def _name_sub(m):
    nonlocal changed
    old = m.group(1)
    new = old.replace(BONDOTO, LEIFER)
    if new != old:
      changed = True
      updates["project.name"] = {"old": old, "new": new}
    return f'name = "{new}"'

  text2 = name_re.sub(_name_sub, text)

  # Console scripts (entry points)
  ep_re = re.compile(r'(?m)^\s*([a-zA-Z0-9_\-]+)\s*=\s*"(.*?)"\s*$')

  def _ep_sub(m):
    nonlocal changed
    key, val = m.group(1), m.group(2)
    new_val = val.replace(f"{BONDOTO}.", f"{LEIFER}.")
    if new_val != val:
      changed = True
      updates.setdefault("entry_points", []).append({"old": val, "new": new_val})
    return f'{key} = "{new_val}"'

  text3 = ep_re.sub(_ep_sub, text2)

  if changed:
    pyproj_path.write_text(text3, encoding="utf-8")
  return changed, updates


def move_package_dir(repo_root: Path) -> tuple[bool, str]:
  src_dir = repo_root / "src"
  old = src_dir / BONDOTO
  new = src_dir / LEIFER
  if old.exists() and old.is_dir():
    if new.exists():
      return False, f"target exists: {new}"
    shutil.move(str(old), str(new))
    return True, f"moved {old} → {new}"
  return False, "no src/bondoto directory found"


def should_visit_file(p: Path) -> bool:
  # skip if any ancestor is excluded
  if any(part in EXCLUDE_DIRS for part in p.parts):
    return False
  # only operate on known code/text extensions
  return p.suffix in CODE_EXTS


def rewrite_tree(repo_root: Path, dry_run: bool) -> dict:
  stats = {
    "files_seen": 0,
    "files_changed": 0,
    "imports_rewritten": 0,
    "renamed": False,
    "rename_msg": "",
    "pyproject_changed": False,
    "updates": {}
  }

  # rename package dir (your existing function)
  renamed, msg = move_package_dir(repo_root) if not dry_run else (
    False, "dry-run: skipped dir move")
  stats["renamed"] = renamed
  stats["rename_msg"] = msg

  # walk with pruning so we never descend into excluded dirs
  for root, dirs, files in os.walk(repo_root, topdown=True):
    # prune in-place (prevents descent)
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for name in files:
      p = Path(root) / name
      if not should_visit_file(p):
        continue

      stats["files_seen"] += 1

      if p.suffix in CODE_EXTS:
        try:
          text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
          # binary or undecodable; skip safely
          continue

        new, n = replace_imports(text)
        if n > 0:
          stats["imports_rewritten"] += n
          if not dry_run:
            p.write_text(new, encoding="utf-8")
          stats["files_changed"] += 1

  # patch pyproject (unchanged from your version)
  changed, updates = (False, {})
  if not dry_run:
    changed, updates = patch_pyproject(repo_root / "pyproject.toml")
  stats["pyproject_changed"] = changed
  stats["updates"] = updates

  return stats


def main():
  ap = argparse.ArgumentParser(
    description="Refactor bondoto → leifer across a single repo.")
  ap.add_argument("--repo", default=".", help="Path to repo root")
  ap.add_argument("--dry-run", action="store_true", help="Do not write changes")
  ap.add_argument("--json", action="store_true", help="Print JSON summary")
  args = ap.parse_args()

  repo_root = Path(args.repo).resolve()
  stats = rewrite_tree(repo_root, args.dry_run)

  if args.json:
    print(json.dumps(stats, indent=2))
  else:
    print(f"Processed repo: {repo_root}")
    print(
      f"Files seen: {stats['files_seen']}, files changed: {stats['files_changed']}, imports rewritten: {stats['imports_rewritten']}"
    )
    print(f"Rename: {stats['renamed']} ({stats['rename_msg']})")
    print(f"pyproject changed: {stats['pyproject_changed']}")
    if stats["updates"]:
      print("Updates:", json.dumps(stats["updates"], indent=2))


if __name__ == "__main__":
  main()
