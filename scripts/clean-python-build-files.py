#!/usr/bin/env python3
import os
import shutil
import fnmatch
import argparse


def clean_python_build_files(directory: str, dry_run: bool = False):
  """
  Finds and deletes common Python build files and directories within a specified directory.

  Args:
      directory (str): The path to the directory to clean.
      dry_run (bool): If True, only print what would be deleted.
  """
  if not os.path.isdir(directory):
    print(f"Error: Directory '{directory}' not found.")
    return

  print(f"{'Dry-run: ' if dry_run else ''}Cleaning build files in: {directory}\n")

  patterns_to_delete = [
    "__pycache__",
    ".pytest_cache",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "build",
    "dist",
    "*.egg-info",
    ".coverage",
    ".tox",
  ]

  deleted_files = 0
  deleted_dirs = 0

  for root, dirs, files in os.walk(directory):
    # Directories
    for d in list(dirs):
      for pattern in patterns_to_delete:
        if fnmatch.fnmatch(d, pattern):
          path_to_delete = os.path.join(root, d)
          print(f"Deleting directory: {path_to_delete}")
          if not dry_run:
            shutil.rmtree(path_to_delete, ignore_errors=True)
          deleted_dirs += 1
          dirs.remove(d)
          break

    # Files
    for f in files:
      for pattern in patterns_to_delete:
        if fnmatch.fnmatch(f, pattern):
          path_to_delete = os.path.join(root, f)
          print(f"Deleting file: {path_to_delete}")
          if not dry_run:
            try:
              os.remove(path_to_delete)
            except OSError as e:
              print(f"  Warning: could not delete {path_to_delete}: {e}")
          deleted_files += 1
          break

  print("\nSummary:")
  print(f"  Directories {'found' if dry_run else 'deleted'}: {deleted_dirs}")
  print(f"  Files {'found' if dry_run else 'deleted'}: {deleted_files}")
  print(f"{'No changes made (dry-run mode).' if dry_run else 'Cleanup complete.'}")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description=
    "Clean Python build artifacts (e.g., __pycache__, *.pyc, dist/, build/, etc.).")
  parser.add_argument(
    "--target-dir",
    type=str,
    default=os.getcwd(),
    help="Directory to clean (default: current working directory).",
  )
  parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Show what would be deleted without actually deleting anything.",
  )

  args = parser.parse_args()
  clean_python_build_files(args.target_dir, dry_run=args.dry_run)
