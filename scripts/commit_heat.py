import argparse
import subprocess
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import os
from pathlib import Path
import glob
"""
Useful to generate a github(ish) style activity heatmap
"""


def parse_args():
  parser = argparse.ArgumentParser(description="Generate Git-style commit heatmap")

  source = parser.add_mutually_exclusive_group(required=True)
  source.add_argument("--input",
                      help="Path to file with commit dates (YYYY-MM-DD, one per line)")
  source.add_argument("--git-dir",
                      help="Path to a Git repo (or top-level dir with sub-repos)")

  parser.add_argument("--output",
                      required=True,
                      help="Path to output image (e.g., heatmap.svg)")
  parser.add_argument("--theme",
                      choices=["light", "dark"],
                      default="light",
                      help="Color theme")
  parser.add_argument("--style",
                      choices=["gradient", "github"],
                      default="gradient",
                      help="Color style")
  parser.add_argument("--transparent",
                      action="store_true",
                      help="Transparent background")
  parser.add_argument("--title",
                      default="Dev Activity (Last 12 Months)",
                      help="Custom chart title")

  return parser.parse_args()


def load_commit_dates_from_file(path):
  with open(path) as f:
    return [line.strip() for line in f if line.strip()]


def extract_git_dates(repo_path):
  try:
    result = subprocess.run([
      "git", "-C", repo_path, "log", "--since=1.year", "--date=short",
      "--pretty=format:%ad"
    ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            check=True)
    return result.stdout.strip().split("\n")
  except subprocess.CalledProcessError:
    return []


def load_commit_dates_from_git(git_dir):
  all_dates = []

  paths = []
  if "*" in git_dir or "?" in git_dir or "[" in git_dir:
    # Glob pattern
    paths = [Path(p) for p in glob.glob(git_dir) if Path(p).is_dir()]
  else:
    paths = [Path(git_dir)]

  for path in paths:
    if (path / ".git").exists():
      all_dates.extend(extract_git_dates(str(path)))
    else:
      # Look inside subdirectories (1 level deep)
      for sub in path.iterdir():
        if (sub / ".git").exists():
          all_dates.extend(extract_git_dates(str(sub)))

  return all_dates


def build_heatmap_data(dates):
  counts = Counter(dates)
  today = datetime.today().date()
  start = today - timedelta(days=364)

  heatmap = np.zeros((7, 53))

  for i in range(365):
    day = start + timedelta(days=i)
    week = i // 7
    dow = day.weekday()
    heatmap[dow, week] = counts.get(str(day), 0)

  return heatmap, start


def get_colormap(theme, style):
  if style == "github":
    if theme == "light":
      return mcolors.ListedColormap(
        ["#ebedf0", "#c6e48b", "#7bc96f", "#239a3b", "#196127"])
    else:
      return mcolors.ListedColormap(
        ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"])
  else:
    return "Greens" if theme == "light" else mcolors.LinearSegmentedColormap.from_list(
      "dark_green", ["#0d1117", "#003d00", "#006600", "#00cc00"])


def render_heatmap(heatmap,
                   start_date,
                   output_path,
                   theme="light",
                   style="gradient",
                   transparent=False,
                   title=""):
  fig, ax = plt.subplots(figsize=(14, 4))

  cmap = get_colormap(theme, style)
  im = ax.imshow(heatmap, cmap=cmap, aspect="auto", interpolation="nearest")

  # Axis labels
  ax.set_yticks(range(7))
  ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                     color="white" if theme == "dark" else "black")

  weeks = [start_date + timedelta(days=7 * i) for i in range(53)]
  month_labels = []
  month_ticks = []

  for i, date in enumerate(weeks):
    if date.day <= 7:  # only show label at start of month
      month_labels.append(date.strftime('%b'))
      month_ticks.append(i)

  ax.set_xticks(month_ticks)
  ax.set_xticklabels(month_labels, color="white" if theme == "dark" else "black")

  # Turn off spines and ticks
  for spine in ax.spines.values():
    spine.set_visible(False)
  ax.tick_params(axis='both', length=0)

  # Title
  ax.set_title(title,
               fontsize=14,
               pad=12,
               color="white" if theme == "dark" else "black")

  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  plt.savefig(output_path, bbox_inches="tight", dpi=150, transparent=transparent)
  print(f"[✓] Saved heatmap to {output_path}")


def main():
  args = parse_args()
  if args.input:
    dates = load_commit_dates_from_file(args.input)
  else:
    dates = load_commit_dates_from_git(args.git_dir)

  if not dates:
    print("[!] No commit dates found.")
    return

  heatmap, start_date = build_heatmap_data(dates)
  render_heatmap(heatmap,
                 start_date,
                 args.output,
                 theme=args.theme,
                 style=args.style,
                 transparent=args.transparent,
                 title=args.title)


if __name__ == "__main__":
  main()
