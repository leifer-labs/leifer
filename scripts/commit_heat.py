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
  parser.add_argument("--title", default="Dev Activity", help="Custom chart title")
  parser.add_argument(
    "--range",
    default=9,
    help="Range for the activity in months",
    type=int,
  )

  return parser.parse_args()


def extract_git_dates(repo_path, range_months):
  try:
    result = subprocess.run([
      "git", "-C", repo_path, "log", f"--since={range_months}.months", "--date=short",
      "--pretty=format:%ad"
    ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            check=True)
    return result.stdout.strip().split("\n")
  except subprocess.CalledProcessError:
    return []


def load_commit_dates_from_git(git_dir, range_months: int):
  all_dates = []

  paths = []
  if "*" in git_dir or "?" in git_dir or "[" in git_dir:
    # Glob pattern
    paths = [Path(p) for p in glob.glob(git_dir) if Path(p).is_dir()]
  else:
    paths = [Path(git_dir)]

  for path in paths:
    if (path / ".git").exists():
      all_dates.extend(extract_git_dates(str(path), range_months))
    else:
      # Look inside subdirectories (1 level deep)
      for sub in path.iterdir():
        if (sub / ".git").exists():
          all_dates.extend(extract_git_dates(str(sub), range_months))

  return all_dates


def build_heatmap_data(dates, range_months):
  counts = Counter(dates)
  today = datetime.today().date()
  start = today - timedelta(days=(range_months * 30))

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
                   title="",
                   range_months: int = None):
  fig, ax = plt.subplots(figsize=(14, 4))
  #fig, ax = plt.subplots(figsize=(11, 7))

  cmap = get_colormap(theme, style)
  im = ax.imshow(heatmap, cmap=cmap, aspect="equal", interpolation="nearest")
  #im = ax.imshow(heatmap, cmap=cmap, aspect="auto", interpolation="nearest")

  # Axis labels
  #week_range = range_months * 4 + 1  #more or less
  week_range = 53
  ax.set_yticks(range(7))
  ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                     color="white" if theme == "dark" else "black")

  weeks = [start_date + timedelta(days=7 * i) for i in range(week_range)]
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
  dates = load_commit_dates_from_git(args.git_dir, args.range)

  if not dates:
    print("[!] No commit dates found.")
    return

  heatmap, start_date = build_heatmap_data(dates, args.range)
  render_heatmap(heatmap,
                 start_date,
                 args.output,
                 theme=args.theme,
                 style=args.style,
                 transparent=args.transparent,
                 title=args.title,
                 range_months=args.range)


if __name__ == "__main__":
  main()
