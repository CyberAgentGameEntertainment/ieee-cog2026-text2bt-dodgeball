"""
Collect BehaviorTree.json files from experiment results and organize them into a single folder
"""
import argparse
import pathlib
import shutil
import sys


def collect_behavior_trees(experiment_dir: pathlib.Path, output_folder_name: str = "behavior_trees"):
    """
    Collect BehaviorTree.json files from each task directory and organize them into a single folder
    
    Args:
        experiment_dir: Path to the experiment results directory
        output_folder_name: Name of the output folder (default: "behavior_trees")
    """
    experiment_dir = pathlib.Path(experiment_dir)
    
    if not experiment_dir.exists():
        print(f"Error: Directory does not exist: {experiment_dir}")
        sys.exit(1)
    
    if not experiment_dir.is_dir():
        print(f"Error: Path is not a directory: {experiment_dir}")
        sys.exit(1)
    
    # Create output directory
    output_dir = experiment_dir / output_folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all directories containing BehaviorTree.json
    task_dirs = sorted([d for d in experiment_dir.iterdir() 
                       if d.is_dir() and (d / "BehaviorTree.json").exists() and d.name != output_folder_name])
    
    if not task_dirs:
        print(f"Warning: No directories with BehaviorTree.json found in {experiment_dir}")
        return
    
    print(f"Found {len(task_dirs)} task directories")
    print(f"Output directory: {output_dir}")
    print()
    
    copied_count = 0
    skipped_count = 0
    
    for task_dir in task_dirs:
        task_name = task_dir.name
        bt_json_path = task_dir / "BehaviorTree.json"
        
        if bt_json_path.exists():
            # Create output filename: task_01.json, task_02.json, etc.
            output_filename = f"{task_name}.json"
            output_path = output_dir / output_filename
            
            # Copy the file
            shutil.copy2(bt_json_path, output_path)
            print(f"✓ Copied: {task_name}/BehaviorTree.json → {output_filename}")
            copied_count += 1
        else:
            print(f"✗ Skipped: {task_name}/BehaviorTree.json (not found)")
            skipped_count += 1
    
    print()
    print(f"{'='*60}")
    print(f"Collection completed!")
    print(f"Copied: {copied_count} files")
    print(f"Skipped: {skipped_count} files (not found)")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Collect BehaviorTree.json files from experiment results into a single folder"
    )
    parser.add_argument(
        'experiment_dir',
        type=str,
        help='Path to the experiment results directory (e.g., results/20260210001259_2_no-newnode_newbt_temp0.0)'
    )
    parser.add_argument(
        '--output-folder',
        type=str,
        default='behavior_trees',
        help='Name of the output folder (default: behavior_trees)'
    )
    
    args = parser.parse_args()
    
    collect_behavior_trees(
        experiment_dir=pathlib.Path(args.experiment_dir),
        output_folder_name=args.output_folder
    )


if __name__ == "__main__":
    main()
