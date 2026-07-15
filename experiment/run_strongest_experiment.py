"""
Experiment runner for 'Strongest' task set
Uses each statement from Strongest.md as a user prompt for behavior tree generation
"""
import os
import sys
import pathlib
import argparse
from typing import Optional
from datetime import datetime

# Add parent directory to path to import editor modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "editor"))

from dotenv import load_dotenv
from editor_agent.Agent import run_agent
from editor_agent.Config import CONFIG


class StrongestExperiment:
    """Runs experiments using prompts from Strongest.md"""
    
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
        
    def load_strongest_prompts(self) -> list[str]:
        """
        Load prompts from Strongest.md
        
        Returns:
            List of prompt strings, one per line
        """
        strongest_path = self.docs_dir / "Strongest.md"
        
        if not strongest_path.exists():
            raise FileNotFoundError(f"Strongest.md not found at {strongest_path}")
        
        with open(strongest_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse numbered prompts (e.g., "1. Create a powerful...")
        prompts = []
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and '. ' in line:
                # Extract prompt after "N. "
                prompt = line.split('. ', 1)[1]
                prompts.append(prompt)
        
        return prompts
    
    def setup_environment(self, newnode: bool, newbt: bool, temperature: float, model: str = "gpt"):
        """
        Set up environment variables for the experiment

        Args:
            newnode: Allow new node creation
            newbt: Allow new behavior tree creation
            temperature: LLM temperature
            model: LLM model name
        """
        # Load the base .env file from editor
        env_path = self.editor_dir / ".env"
        load_dotenv(env_path)

        # Override settings
        os.environ["NEWNODE"] = "true" if newnode else "false"
        os.environ["NEWBT"] = "true" if newbt else "false"
        os.environ["TEMPERATURE"] = str(temperature)
        os.environ["MODEL"] = model

        # Reload CONFIG to pick up new environment variables
        CONFIG.NEWNODE = newnode
        CONFIG.NEWBT = newbt
        CONFIG.TEMPERATURE = temperature
        CONFIG.MODEL = model
    
    def run_experiment(
        self,
        newnode: bool = False,
        newbt: bool = True,
        temperature: float = 1.0,
        num_repeats: int = 1,
        prompt_indices: Optional[list[int]] = None,
        dry_run: bool = False,
        model: str = "gpt",
    ):
        """
        Run the strongest experiment
        
        Args:
            newnode: Allow new node creation
            newbt: Allow new behavior tree creation
            temperature: LLM temperature
            num_repeats: Number of times to repeat each prompt
            prompt_indices: Specific prompt indices to run (1-based, None = all)
            dry_run: If True, only print what would be done
        """
        # Set up environment
        self.setup_environment(newnode, newbt, temperature, model)

        # Load prompts
        prompts = self.load_strongest_prompts()

        # Filter prompts if specific indices requested
        if prompt_indices:
            filtered_prompts = []
            for idx in prompt_indices:
                if 1 <= idx <= len(prompts):
                    filtered_prompts.append((idx, prompts[idx - 1]))
                else:
                    print(f"Warning: Prompt index {idx} out of range (1-{len(prompts)})")
            prompts_to_run = filtered_prompts
        else:
            prompts_to_run = [(i + 1, prompt) for i, prompt in enumerate(prompts)]

        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        model_str = model.replace(":", "-")
        config_str = f"strongest_newnode{newnode}_newbt{newbt}_temp{temperature}_rep{num_repeats}_{model_str}"
        folder_name = f"{timestamp}_{config_str}"
        output_dir = self.results_dir / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"=== Strongest Experiment Configuration ===")
        print(f"NEWNODE: {newnode}")
        print(f"NEWBT: {newbt}")
        print(f"Temperature: {temperature}")
        print(f"Model: {model}")
        print(f"Number of Repeats: {num_repeats}")
        print(f"Output Directory: {output_dir}")
        print(f"Number of Prompts: {len(prompts_to_run)}")
        print(f"Dry Run: {dry_run}")
        print()
        
        # Process each prompt
        for prompt_num, prompt in prompts_to_run:
            print(f"\n{'='*60}")
            print(f"Prompt {prompt_num}/{len(prompts)}: {prompt[:50]}...")
            print(f"{'='*60}")
            
            for repeat in range(num_repeats):
                if num_repeats > 1:
                    print(f"\n--- Repeat {repeat + 1}/{num_repeats} ---")
                
                if dry_run:
                    print(f"[DRY RUN] Would run prompt: {prompt}")
                    continue
                
                # Reset Unity project before each run
                self._reset_unity_project()
                
                try:
                    # Run the agent
                    print(f"Running agent with prompt: {prompt[:80]}...")
                    agent_result = run_agent(prompt)
                    
                    print(f"Agent completed:")
                    print(f"  - BT Generated: {agent_result.get('bt_generated', False)}")
                    print(f"  - BT Error: {agent_result.get('bt_error', True)}")
                    print(f"  - C# Error: {agent_result.get('csharp_error', True)}")
                    
                    # Copy generated files
                    self._copy_generated_files(
                        prompt_num=prompt_num,
                        prompt_text=prompt,
                        output_dir=output_dir,
                        agent_result=agent_result,
                        repeat_idx=repeat
                    )
                    
                    # Copy log file
                    self._copy_latest_log(output_dir, prompt_num, repeat)
                    
                except Exception as e:
                    print(f"Error running agent for prompt {prompt_num}: {e}")
                    import traceback
                    traceback.print_exc()
                    
        print(f"\n{'='*60}")
        print("Strongest Experiment completed!")
        print(f"Results saved to: {output_dir}")
        print(f"{'='*60}")
    
    def _copy_generated_files(
        self, 
        prompt_num: int, 
        prompt_text: str,
        output_dir: pathlib.Path, 
        agent_result: dict, 
        repeat_idx: int = 0
    ):
        """
        Copy generated behavior tree files to the output directory
        
        Args:
            prompt_num: The prompt number (1-based)
            prompt_text: The full prompt text
            output_dir: Output directory for results
            agent_result: Result dict from run_agent execution
            repeat_idx: Index of the repeat (0-based)
        """
        import json
        import shutil
        
        project_dir = pathlib.Path(os.getenv("PROJECT_DIRECTORY"))
        bt_dir = project_dir / "Assets" / "BehaviorTree"
        
        # Create task-specific subdirectory with repeat index
        if repeat_idx > 0:
            task_dir = output_dir / f"prompt_{prompt_num:02d}_repeat_{repeat_idx + 1}"
        else:
            task_dir = output_dir / f"prompt_{prompt_num:02d}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Save prompt metadata with agent results
        metadata = {
            "prompt_number": prompt_num,
            "prompt_text": prompt_text,
            "timestamp": datetime.now().isoformat(),
            "repeat_index": repeat_idx,
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
            dest_bt_json = task_dir / "BehaviorTree.json"
            shutil.copy2(bt_json_path, dest_bt_json)
            print(f"Copied BehaviorTree.json → {task_dir.name}/BehaviorTree.json")
        else:
            print(f"Warning: BehaviorTree.json not found at {bt_json_path}")
        
        # Copy BehaviorTreePlan.txt if exists
        bt_plan_path = bt_dir / "BehaviorTreePlan.txt"
        if bt_plan_path.exists():
            dest_bt_plan = task_dir / "BehaviorTreePlan.txt"
            shutil.copy2(bt_plan_path, dest_bt_plan)
            print(f"Copied BehaviorTreePlan.txt → {task_dir.name}/BehaviorTreePlan.txt")
        
        # Copy all C# files in BehaviorTree directory if newnode is enabled
        if CONFIG.NEWNODE and bt_dir.exists():
            cs_files = list(bt_dir.glob("*.cs"))
            for cs_file in cs_files:
                dest_cs = task_dir / cs_file.name
                shutil.copy2(cs_file, dest_cs)
                print(f"Copied {cs_file.name} → {task_dir.name}/{cs_file.name}")
    
    def _copy_latest_log(self, output_dir: pathlib.Path, prompt_num: int, repeat_idx: int = 0):
        """
        Copy the latest log file from editor/logs/ to the output directory
        
        Args:
            output_dir: Output directory for results
            prompt_num: Prompt number being processed
            repeat_idx: Index of the repeat (0-based)
        """
        import shutil
        
        logs_dir = self.editor_dir / "logs"
        
        if not logs_dir.exists():
            print(f"Warning: Logs directory not found at {logs_dir}")
            return
        
        # Find the most recent .log file
        log_files = sorted(logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not log_files:
            print(f"Warning: No log files found in {logs_dir}")
            return
        
        latest_log = log_files[0]
        
        # Copy to task subdirectory
        if repeat_idx > 0:
            task_dir = output_dir / f"prompt_{prompt_num:02d}_repeat_{repeat_idx + 1}"
        else:
            task_dir = output_dir / f"prompt_{prompt_num:02d}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        dest_log = task_dir / "agent_log.log"
        shutil.copy2(latest_log, dest_log)
        print(f"Copied log file → {task_dir.name}/agent_log.log")
    
    def _reset_unity_project(self):
        """
        Reset Unity project by removing the BehaviorTree directory
        This removes all generated files
        """
        import shutil
        
        project_dir = pathlib.Path(os.getenv("PROJECT_DIRECTORY"))
        bt_dir = project_dir / "Assets" / "BehaviorTree"
        
        if bt_dir.exists():
            print(f"Resetting Unity project: Removing {bt_dir}")
            shutil.rmtree(bt_dir)
            print("Unity project reset complete")
        else:
            print("Unity project already clean (no BehaviorTree directory)")


def str_to_bool(v):
    """Convert string to boolean"""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected (true/false)')


def main():
    """Main entry point for running strongest experiments"""
    parser = argparse.ArgumentParser(
        description="Run 'Strongest' experiment using prompts from Strongest.md"
    )
    parser.add_argument('--newnode', type=str_to_bool, required=True,
                       help='Allow C# node creation (required: true/false)')
    parser.add_argument('--newbt', type=str_to_bool, required=True,
                       help='Allow behavior tree creation (required: true/false)')
    parser.add_argument('--temperature', type=float, default=1.0,
                       help='LLM temperature setting (default: 1.0)')
    parser.add_argument('--repeats', type=int, default=1,
                       help='Number of times to repeat each prompt (default: 1)')
    parser.add_argument('--prompts', type=int, nargs='+',
                       help='Specific prompt numbers to run (1-based, default: all)')
    parser.add_argument('--model', type=str, default="gpt",
                       help='LLM model name or alias: gpt=gpt-5.2-2025-12-11, claude=claude-sonnet-4-6, gemini=gemini-2.5-pro')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run without execution')

    args = parser.parse_args()

    runner = StrongestExperiment()

    runner.run_experiment(
        newnode=args.newnode,
        newbt=args.newbt,
        temperature=args.temperature,
        num_repeats=args.repeats,
        prompt_indices=args.prompts,
        dry_run=args.dry_run,
        model=args.model,
    )


if __name__ == "__main__":
    main()
