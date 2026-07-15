"""Plot histogram of `win_rate_percent` from CSV.

Usage:
  python writing/data/winrates_hist.py
  python writing/data/winrates_hist.py --csv writing/data/winrates.csv --out writing/data/winrates_hist.png
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


def plot_hist(values, bins='auto', outpath=None, show=True):
	fig, ax = plt.subplots(figsize=(8, 5))
	ax.hist(values, bins=bins, color="#C0C0C0", edgecolor='black')
	ax.set_xlabel('Win Rates (%)')
	ax.set_ylabel('Count')
	ax.grid(axis='y', alpha=0.6)

	if outpath:
		outdir = os.path.dirname(outpath)
		if outdir:
			os.makedirs(outdir, exist_ok=True)
		fig.savefig(outpath, dpi=150, bbox_inches='tight')
		print(f"Saved histogram to {outpath}")

	if show:
		plt.show()
	plt.close(fig)


def main():
	parser = argparse.ArgumentParser(description='Plot histogram of win_rate_percent from CSV')
	parser.add_argument('--csv', default=os.path.join('data', 'winrates.csv'), help='Path to CSV file')
	parser.add_argument('--bins', default='auto', help='Number of bins (int) or "auto"')
	parser.add_argument('--out', default=os.path.join('data', 'winrates_hist.png'), help='Output image path')
	parser.add_argument('--no-show', dest='show', action='store_false', help='Do not display the plot interactively')
	args = parser.parse_args()

	vals = load_winrates(args.csv)
	if not vals:
		print(f'No numeric data loaded from {args.csv}', file=sys.stderr)
		return

	# Calculate and output statistics
	mean_val = statistics.mean(vals)
	median_val = statistics.median(vals)
	print(f'Mean (平均値): {mean_val:.2f}%')
	print(f'Median (中央値): {median_val:.2f}%')
	print()

	bins = [i for i in range(0, 101, 10)]

	plot_hist(vals, bins=bins, outpath=args.out, show=args.show)


if __name__ == '__main__':
	main()

