"""
Experiment runner for generating behavior trees using the editor agent
"""
import os
import sys
import json
import argparse
import pathlib
import shutil
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from collections import Counter

# Add parent directory to path to import editor modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "editor"))

from dotenv import load_dotenv
from editor_agent.Agent import run_agent
from editor_agent.Config import CONFIG


@dataclass
class Task:
    """Represents a single task"""
    task_number: int
    name: str
    level1_prompt: str
    level2_prompt: list[str]  # Now a list of variations


@dataclass
class ExperimentConfig:
    """Configuration for an experiment run"""
    level: int  # 1 or 2
    newnode: bool
    newbt: bool
    temperature: float = 1.0
    num_repeats: int = 1
    model: str = "gpt"

    def to_folder_name(self) -> str:
        """Generate folder name based on configuration"""
        newnode_str = "newnode" if self.newnode else "no-newnode"
        newbt_str = "newbt" if self.newbt else "no-newbt"
        temp_str = f"temp{self.temperature}"
        model_str = self.model.replace(":", "-")
        return f"{self.level}_{newnode_str}_{newbt_str}_{temp_str}_{model_str}"


class ExperimentRunner:
    """Runs experiments to generate behavior trees for tasks"""
    
    def __init__(self, base_dir: Optional[pathlib.Path] = None):
        """
        Initialize the experiment runner
        
        Args:
            base_dir: Base directory for the experiment (defaults to current file's parent)
        """
        if base_dir is None:
            base_dir = pathlib.Path(__file__).parent
        
        self.base_dir = base_dir
        self.docs_dir = base_dir.parent / "docs" / "tasks"
        self.results_dir = base_dir / "results"
        self.editor_dir = base_dir.parent / "editor"
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_environment(self, config: ExperimentConfig):
        """
        Set up environment variables for the experiment
        
        Args:
            config: Experiment configuration
        """
        # Load the base .env file from editor
        env_path = self.editor_dir / ".env"
        load_dotenv(env_path)
        
        # Override NEWNODE, NEWBT, TEMPERATURE and MODEL settings
        os.environ["NEWNODE"] = "true" if config.newnode else "false"
        os.environ["NEWBT"] = "true" if config.newbt else "false"
        os.environ["TEMPERATURE"] = str(config.temperature)
        os.environ["MODEL"] = config.model

        # Reload CONFIG to pick up new environment variables
        CONFIG.NEWNODE = config.newnode
        CONFIG.NEWBT = config.newbt
        CONFIG.TEMPERATURE = config.temperature
        CONFIG.MODEL = config.model
    
    def run_experiment(
        self,
        config: ExperimentConfig,
        task_numbers: Optional[list[int]] = None,
        dry_run: bool = False
    ):
        """
        Run the experiment for specified tasks
        
        Args:
            config: Experiment configuration
            task_numbers: List of task numbers to run (None = all tasks)
            dry_run: If True, only print what would be done without executing
        """
        # Set up environment
        self.setup_environment(config)
        
        # Load tasks from JSON
        tasks_json_path = self.base_dir / "tasks.json"
        with open(tasks_json_path, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        # Convert to Task objects
        # Auto-assign task numbers starting from 1 if not present
        if task_numbers is None:
            enumerator = enumerate(tasks_data['tasks'])
        else:
            enumerator = [(idx-1, tasks_data['tasks'][idx-1]) for idx in task_numbers]
        tasks = [
            Task(
                task_number=(idx + 1),
                name=t['name'],
                level1_prompt=t['level1_prompt'],
                level2_prompt=t['level2_prompt'] if isinstance(t['level2_prompt'], list) else [t['level2_prompt']]
            )
            for idx, t in enumerator
        ]
        
        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        folder_name = f"{timestamp}_{config.to_folder_name()}"
        output_dir = self.results_dir / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"=== Experiment Configuration ===")
        print(f"Level: {config.level}")
        print(f"NEWNODE: {config.newnode}")
        print(f"NEWBT: {config.newbt}")
        print(f"Temperature: {config.temperature}")
        print(f"Model: {config.model}")
        print(f"Number of Repeats: {config.num_repeats}")
        print(f"Output Directory: {output_dir}")
        print(f"Number of Tasks: {len(tasks)}")
        print(f"Dry Run: {dry_run}")
        print()
        
        # Process each task
        for task in tasks:
            print(f"\n{'='*60}")
            print(f"Processing Task {task.task_number}: {task.name}")
            print(f"{'='*60}")
            
            # Determine which prompts to use based on level
            if config.level == 1:
                prompts_to_run = [(task.level1_prompt, None)]  # (prompt, variation_index)
            else:  # level == 2
                # Use all level2 variations
                prompts_to_run = [(prompt, idx) for idx, prompt in enumerate(task.level2_prompt)]
            
            print(f"Number of prompt variations: {len(prompts_to_run)}")
            
            # Process each prompt variation
            for prompt_idx, (base_prompt, variation_idx) in enumerate(prompts_to_run, 1):
                if config.level == 2 and variation_idx is not None:
                    print(f"\n  --- Variation {variation_idx + 1}/{len(prompts_to_run)} ---")
                
                # Run multiple times if repeats > 1
                for repeat_idx in range(config.num_repeats):
                    if config.num_repeats > 1:
                        print(f"\n  Repeat {repeat_idx + 1}/{config.num_repeats}")
                    
                    self._reset_unity_project()
                    print("  Unity project reset")
                    
                    # Get the appropriate prompt based on level
                    prompt = base_prompt
                    
                    # Add prefix to level 1 prompts
                    if config.level == 1:
                        prompt = "Implement the behavior tree identical with the structure below:\n" + prompt
                    
                    print(f"\n  Prompt:\n  {prompt[:100]}...\n")
                    
                    if dry_run:
                        print("  [DRY RUN] Skipping execution")
                        continue
                    
                    try:
                        # Run the agent
                        print("  Running editor agent...")
                        result = run_agent(user_input=prompt)
                        
                        # Extract state information
                        bt_generated = result.get('bt_generated', False)
                        bt_error = result.get('bt_error', True)
                        csharp_error = result.get('csharp_error', True)
                        
                        print(f"\n  Agent Execution Results:")
                        print(f"    BehaviorTree Generated: {bt_generated}")
                        print(f"    BehaviorTree Valid: {not bt_error}")
                        print(f"    C# Compilation: {'OK' if not csharp_error else 'Errors'}")
                        
                        # Calculate effective repeat index for file naming
                        # For level2: variation * num_repeats + repeat
                        effective_repeat_idx = repeat_idx
                        if config.level == 2 and variation_idx is not None:
                            effective_repeat_idx = variation_idx * config.num_repeats + repeat_idx
                        
                        # Copy generated files and logs to output directory
                        self._copy_generated_files(task, output_dir, result, effective_repeat_idx)
                        self._copy_latest_log(output_dir, task.task_number, effective_repeat_idx)
                        
                        if bt_generated and not bt_error:
                            print(f"  ✓ Completed successfully")
                        else:
                            print(f"  ⚠ Completed with issues")
                        
                    except Exception as e:
                        print(f"  ✗ Error: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                    
        print(f"\n{'='*60}")
        print("Experiment completed!")
        print(f"Results saved to: {output_dir}")
        print(f"{'='*60}")
        
        # Analyze JSON isomorphism if repeats >= 2
        if config.num_repeats >= 2:
            self._analyze_json_isomorphism(output_dir, tasks, config.num_repeats)
    
    def _copy_generated_files(self, task: Task, output_dir: pathlib.Path, agent_result: dict, repeat_idx: int = 0):
        """
        Copy generated behavior tree files to the output directory
        
        Args:
            task: The task that was processed
            output_dir: Output directory for results
            agent_result: Result dict from run_agent execution
            repeat_idx: Index of the repeat (0-based)
        """
        project_dir = pathlib.Path(os.getenv("PROJECT_DIRECTORY"))
        bt_dir = project_dir / "Assets" / "BehaviorTree"
        
        # Create task-specific subdirectory with repeat index
        if repeat_idx > 0:
            task_dir = output_dir / f"task_{task.task_number:02d}_repeat{repeat_idx + 1:02d}"
        else:
            task_dir = output_dir / f"task_{task.task_number:02d}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Save task metadata with agent results
        metadata = {
            "task_number": task.task_number,
            "name": task.name,
            "timestamp": datetime.now().isoformat(),
            "agent_result": {
                "bt_generated": agent_result.get('bt_generated', False),
                "bt_error": agent_result.get('bt_error', True),
                "csharp_error": agent_result.get('csharp_error', True),
            }
        }
        metadata_path = task_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Copy BehaviorTree.json if exists
        bt_json_path = bt_dir / "BehaviorTree.json"
        if bt_json_path.exists():
            output_json = task_dir / "BehaviorTree.json"
            shutil.copy2(bt_json_path, output_json)
            print(f"Copied BehaviorTree.json → {task_dir.name}/BehaviorTree.json")
        else:
            print("Warning: BehaviorTree.json not found")
        
        # Copy BehaviorTreePlan.txt if exists
        bt_plan_path = bt_dir / "BehaviorTreePlan.txt"
        if bt_plan_path.exists():
            output_plan = task_dir / "BehaviorTreePlan.txt"
            shutil.copy2(bt_plan_path, output_plan)
            print(f"Copied BehaviorTreePlan.txt → {task_dir.name}/BehaviorTreePlan.txt")
        
        # Copy all C# files in BehaviorTree directory if newnode is enabled
        if CONFIG.NEWNODE and bt_dir.exists():
            cs_files = list(bt_dir.rglob("*.cs"))
            if cs_files:
                cs_dir = task_dir / "CSharp"
                cs_dir.mkdir(parents=True, exist_ok=True)
                for cs_file in cs_files:
                    rel_path = cs_file.relative_to(bt_dir)
                    output_cs = cs_dir / rel_path
                    output_cs.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(cs_file, output_cs)
                print(f"Copied {len(cs_files)} C# files → {task_dir.name}/CSharp/")
    
    def _copy_latest_log(self, output_dir: pathlib.Path, task_number: int, repeat_idx: int = 0):
        """
        Copy the latest log file from editor/logs/ to the output directory
        
        Args:
            output_dir: Output directory for results
            task_number: Task number being processed
            repeat_idx: Index of the repeat (0-based)
        """
        editor_dir = pathlib.Path(__file__).parent.parent / "editor"
        logs_dir = editor_dir / "logs"
        
        if not logs_dir.exists():
            print("Warning: Logs directory not found")
            return
        
        # Find the most recent .log file
        log_files = sorted(logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not log_files:
            print("Warning: No log files found")
            return
        
        latest_log = log_files[0]
        
        # Copy to task subdirectory
        if repeat_idx > 0:
            task_dir = output_dir / f"task_{task_number:02d}_repeat{repeat_idx + 1:02d}"
        else:
            task_dir = output_dir / f"task_{task_number:02d}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        dest_log = task_dir / f"agent_log.log"
        shutil.copy2(latest_log, dest_log)
        print(f"Copied log file → {task_dir.name}/agent_log.log")
    
    def _reset_unity_project(self):
        """
        Reset Unity project by removing the BehaviorTree directory
        This removes all generated files
        """
        project_dir = pathlib.Path(os.getenv("PROJECT_DIRECTORY"))
        bt_dir = project_dir / "Assets" / "BehaviorTree"
        
        if bt_dir.exists():
            try:
                shutil.rmtree(bt_dir)
                print(f"✓ Removed generated files: {bt_dir.relative_to(project_dir)}")
            except Exception as e:
                print(f"Warning: Failed to remove directory: {e}")
        else:
            print("✓ BehaviorTree directory already clean")
    
    def _compare_json_files(self, json_path1: pathlib.Path, json_path2: pathlib.Path) -> bool:
        """
        Compare two JSON files for structural and value equality
        
        Args:
            json_path1: Path to first JSON file
            json_path2: Path to second JSON file
            
        Returns:
            True if JSONs are identical in structure and values, False otherwise
        """
        try:
            if not json_path1.exists() or not json_path2.exists():
                return False
            
            with open(json_path1, 'r', encoding='utf-8') as f1:
                data1 = json.load(f1)
            
            with open(json_path2, 'r', encoding='utf-8') as f2:
                data2 = json.load(f2)
            
            return data1 == data2
        except Exception as e:
            print(f"Warning: Failed to compare JSON files: {e}")
            return False
    
    def _normalize_json(self, data) -> str:
        """
        Normalize JSON data to a canonical string representation
        
        Args:
            data: JSON data to normalize
            
        Returns:
            Canonical string representation of the JSON
        """
        return json.dumps(data, sort_keys=True, ensure_ascii=False)
    
    def _analyze_json_isomorphism(self, output_dir: pathlib.Path, tasks: list[Task], num_repeats: int):
        """
        Analyze isomorphism of generated JSONs for each task across repeats
        
        Args:
            output_dir: Directory containing experiment results
            tasks: List of tasks that were executed
            num_repeats: Number of repeats per task
        """
        print(f"\n{'='*60}")
        print("JSON Isomorphism Analysis")
        print(f"{'='*60}")
        
        for task in tasks:
            print(f"\nTask {task.task_number}: {task.name}")
            
            # Collect all JSON files for this task
            json_files = []
            json_data_list = []
            
            for repeat_idx in range(num_repeats):
                if repeat_idx == 0:
                    task_dir = output_dir / f"task_{task.task_number:02d}"
                else:
                    task_dir = output_dir / f"task_{task.task_number:02d}_repeat{repeat_idx + 1:02d}"
                
                json_path = task_dir / "BehaviorTree.json"
                json_files.append(json_path)
                
                if json_path.exists():
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            json_data_list.append(self._normalize_json(data))
                    except Exception as e:
                        print(f"  Warning: Failed to load {json_path.name} from repeat {repeat_idx + 1}: {e}")
                        json_data_list.append(None)
                else:
                    print(f"  Warning: BehaviorTree.json not found for repeat {repeat_idx + 1}")
                    json_data_list.append(None)
            
            # Filter out None values (missing or failed JSONs)
            valid_jsons = [j for j in json_data_list if j is not None]
            
            if not valid_jsons:
                print(f"  No valid JSON files found")
                continue
            
            # Count unique JSONs
            json_counter = Counter(valid_jsons)
            unique_count = len(json_counter)
            
            print(f"  Total repeats: {num_repeats}")
            print(f"  Valid JSONs: {len(valid_jsons)}")
            print(f"  Unique JSONs: {unique_count}")
            
            # Show distribution of identical JSONs
            if unique_count > 1:
                print(f"  Distribution:")
                for idx, (json_str, count) in enumerate(json_counter.most_common(), 1):
                    print(f"    Pattern {idx}: {count} occurrence(s)")
            else:
                print(f"  All valid JSONs are identical")
        
        print(f"\n{'='*60}")


def _str2bool(value: str) -> bool:
    """Parse a boolean from a CLI string (argparse type)"""
    if isinstance(value, bool):
        return value
    if value.lower() in ("true", "t", "yes", "y", "1"):
        return True
    if value.lower() in ("false", "f", "no", "n", "0"):
        return False
    raise argparse.ArgumentTypeError(f"Expected a boolean value, got: {value!r}")


def main():
    """Main entry point for running experiments"""
    parser = argparse.ArgumentParser(description="Run behavior tree generation experiment")
    parser.add_argument('--level', type=int, default=1, choices=[1, 2],
                       help='Prompt level to use (1 or 2)')
    parser.add_argument('--newnode', type=_str2bool, default=False,
                       help='Allow C# node creation')
    parser.add_argument('--newbt', type=_str2bool, default=True,
                       help='(Reserved for future use)')
    parser.add_argument('--temperature', type=float, default=1.0,
                       help='LLM temperature setting (default: 1.0)')
    parser.add_argument('--repeats', type=int, default=1,
                       help='Number of times to repeat each task (default: 1)')
    parser.add_argument('--tasks', type=int, nargs='+',
                       help='Specific task numbers to run (default: all)')
    parser.add_argument('--model', type=str, default="gpt",
                       help='LLM model name or alias: gpt=gpt-5.2-2025-12-11, claude=claude-sonnet-4-6, gemini=gemini-2.5-pro')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run without execution')

    args = parser.parse_args()

    runner = ExperimentRunner()

    config = ExperimentConfig(
        level=args.level,
        newnode=args.newnode,
        newbt=args.newbt,
        temperature=args.temperature,
        num_repeats=args.repeats,
        model=args.model,  # alias resolution happens in _create_llm()
    )
    
    runner.run_experiment(
        config=config,
        task_numbers=args.tasks,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
