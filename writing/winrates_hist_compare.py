# /// script
# requires-python = ">=3.9"
# dependencies = ["matplotlib"]
# ///
"""Plot overlapping histograms comparing win rates of two CSV files.

Usage:
  python writing/winrates_hist_compare.py
  python writing/winrates_hist_compare.py --out writing/data/winrates_hist_compare.png --no-show
"""

import argparse
import csv
import os
import statistics
import sys

import matplotlib.pyplot as plt


def load_winrates(csv_path):
    vals = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                v = row.get('win_rate_percent')
                if v is None:
                    continue
                try:
                    vals.append(float(v))
                except ValueError:
                    continue
    except FileNotFoundError:
        print(f"CSV not found: {csv_path}", file=sys.stderr)
    return vals


def print_stats(label, vals):
    mean_val = statistics.mean(vals)
    median_val = statistics.median(vals)
    print(f"[{label}]  n={len(vals)}  mean={mean_val:.1f}%  median={median_val:.1f}%")


def plot_compare(vals_a, vals_b, label_a, label_b, bins, outpath=None, show=True):
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(vals_a, bins=bins, alpha=0.6, color="#4C72B0", edgecolor='black',
            label=label_a)
    ax.hist(vals_b, bins=bins, alpha=0.6, color="#DD8452", edgecolor='black',
            label=label_b)

    mean_a = statistics.mean(vals_a)
    mean_b = statistics.mean(vals_b)
    ax.axvline(mean_a, color="#4C72B0", linestyle='--', linewidth=1.5,
               label=f"{label_a} mean: {mean_a:.1f}%")
    ax.axvline(mean_b, color="#DD8452", linestyle='--', linewidth=1.5,
               label=f"{label_b} mean: {mean_b:.1f}%")

    ax.set_xlabel('Win Rate (%)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Win Rate Distribution Comparison', fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.5)
    ax.set_xticks(bins)

    fig.tight_layout()

    if outpath:
        outdir = os.path.dirname(outpath)
        if outdir:
            os.makedirs(outdir, exist_ok=True)
        fig.savefig(outpath, dpi=150, bbox_inches='tight')
        print(f"Saved to {outpath}")

    if show:
        plt.show()
    plt.close(fig)


def main():
    here = os.path.dirname(__file__)
    default_csv_a = os.path.join(here, 'data', 'winrates.csv')
    default_csv_b = os.path.join(here, 'data', 'winrates_claude.csv')
    default_out = os.path.join(here, 'data', 'winrates_hist_compare.png')

    parser = argparse.ArgumentParser(description='Compare win rate histograms from two CSVs')
    parser.add_argument('--csv-a', default=default_csv_a, help='First CSV (baseline)')
    parser.add_argument('--csv-b', default=default_csv_b, help='Second CSV (Claude)')
    parser.add_argument('--label-a', default='GPT-5.2', help='Legend label for first CSV')
    parser.add_argument('--label-b', default='Claude', help='Legend label for second CSV')
    parser.add_argument('--out', default=default_out, help='Output image path')
    parser.add_argument('--no-show', dest='show', action='store_false',
                        help='Do not display the plot interactively')
    args = parser.parse_args()

    vals_a = load_winrates(args.csv_a)
    vals_b = load_winrates(args.csv_b)

    if not vals_a:
        print(f"No data loaded from {args.csv_a}", file=sys.stderr)
        return
    if not vals_b:
        print(f"No data loaded from {args.csv_b}", file=sys.stderr)
        return

    print_stats(args.label_a, vals_a)
    print_stats(args.label_b, vals_b)

    bins = list(range(0, 101, 10))
    plot_compare(vals_a, vals_b, args.label_a, args.label_b,
                 bins=bins, outpath=args.out, show=args.show)


if __name__ == '__main__':
    main()
