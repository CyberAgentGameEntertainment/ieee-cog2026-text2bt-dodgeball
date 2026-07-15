"""
Collect all BehaviorTree.json files from a strongest experiment result directory
into a single flat directory.

Output filenames: <subfolder_name>_BehaviorTree.json
e.g. prompt_01_BehaviorTree.json, prompt_01_repeat_2_BehaviorTree.json
"""

import argparse
import shutil
from pathlib import Path


def collect_behavior_trees(result_dir: Path, output_dir: Path) -> None:
    result_dir = result_dir.resolve()
    output_dir = output_dir.resolve()

    if not result_dir.exists():
        raise FileNotFoundError(f"Result directory not found: {result_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    collected = 0
    for bt_file in sorted(result_dir.rglob("BehaviorTree.json")):
        subfolder = bt_file.parent.name
        dest = output_dir / f"{subfolder}_BehaviorTree.json"
        shutil.copy2(bt_file, dest)
        print(f"  {bt_file.relative_to(result_dir)} -> {dest.name}")
        collected += 1

    print(f"\nCollected {collected} BehaviorTree.json files into: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect all BehaviorTree.json files from a strongest experiment result directory."
    )
    parser.add_argument(
        "result_dir",
        type=Path,
        help="Path to the experiment result directory (e.g. results/20260512162941_strongest_...)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output directory (default: <result_dir>/collected_behavior_trees)",
    )
    args = parser.parse_args()

    output_dir = args.output if args.output else args.result_dir / "collected_behavior_trees"
    collect_behavior_trees(args.result_dir, output_dir)


if __name__ == "__main__":
    main()
