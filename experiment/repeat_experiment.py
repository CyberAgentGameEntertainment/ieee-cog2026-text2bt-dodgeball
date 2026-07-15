"""
Repeat experiment: Run the same prompt 10 times with no_newnode condition
"""

import os
import sys
import json
import shutil
import pathlib
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import editor modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "editor"))

from editor_agent.Agent import run_agent
from editor_agent.Config import CONFIG


class RepeatExperimentRunner:
    """Runs the same experiment multiple times to test consistency"""
    
    def __init__(self, base_dir: pathlib.Path = None):
        """
        Initialize the repeat experiment runner
        
        Args:
            base_dir: Base directory for the experiment (defaults to current file's parent)
        """
        if base_dir is None:
            base_dir = pathlib.Path(__file__).parent
        
        self.base_dir = base_dir
        self.results_dir = base_dir / "results"
        self.editor_dir = base_dir.parent / "editor"
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_environment(self, newnode: bool = False, newbt: bool = True, temperature: float = 1.0, model: str = "gpt"):
        """
        Set up environment variables for the experiment

        Args:
            newnode: Allow C# node creation
            newbt: Reserved for future use
            temperature: LLM temperature setting
            model: LLM model name
        """
        # Load the base .env file from editor
        env_path = self.editor_dir / ".env"
        load_dotenv(env_path)

        # Override NEWNODE, NEWBT, TEMPERATURE and MODEL settings
        os.environ["NEWNODE"] = "true" if newnode else "false"
        os.environ["NEWBT"] = "true" if newbt else "false"
        os.environ["TEMPERATURE"] = str(temperature)
        os.environ["MODEL"] = model

        # Reload CONFIG to pick up new environment variables
        CONFIG.NEWNODE = newnode
        CONFIG.NEWBT = newbt
        CONFIG.MODEL = model
    
    def run_repeat_experiment(
        self,
        prompt: str,
        num_repeats: int = 10,
        newnode: bool = False,
        newbt: bool = True,
        temperature: float = 1.0,
        model: str = "gpt",
    ):
        """
        Run the same experiment multiple times

        Args:
            prompt: The prompt to give to the agent
            num_repeats: Number of times to repeat the experiment
            newnode: Allow C# node creation
            newbt: Reserved for future use
            temperature: LLM temperature setting
            model: LLM model name
        """
        # Set up environment
        self.setup_environment(newnode=newnode, newbt=newbt, temperature=temperature, model=model)

        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        newnode_str = "newnode" if newnode else "no_newnode"
        newbt_str = "newbt" if newbt else "no_newbt"
        model_str = model.replace(":", "-")
        folder_name = f"{timestamp}_repeat_{num_repeats}x_{newnode_str}_{newbt_str}_{model_str}"
        output_dir = self.results_dir / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"=== Repeat Experiment Configuration ===")
        print(f"Prompt: {prompt}")
        print(f"Number of Repeats: {num_repeats}")
        print(f"NEWNODE: {newnode}")
        print(f"NEWBT: {newbt}")
        print(f"Temperature: {temperature}")
        print(f"Model: {model}")
        print(f"Output Directory: {output_dir}")
        print()
        
        # Save experiment configuration
        config_data = {
            "prompt": prompt,
            "num_repeats": num_repeats,
            "newnode": newnode,
            "newbt": newbt,
            "temperature": temperature,
            "model": model,
            "timestamp": timestamp,
        }
        config_path = output_dir / "experiment_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        # Run the experiment multiple times
        results_summary = []
        
        for i in range(1, num_repeats + 1):
            print(f"\n{'='*60}")
            print(f"Run {i}/{num_repeats}")
            print(f"{'='*60}")
            
            # Reset Unity project before each run
            self._reset_unity_project()
            print("Unity project reset")
            
            print(f"\nPrompt:\n{prompt}\n")
            
            try:
                # Run the agent
                print("Running editor agent...")
                result = run_agent(user_input=prompt)
                
                # Extract state information
                bt_generated = result.get('bt_generated', False)
                bt_error = result.get('bt_error', True)
                csharp_error = result.get('csharp_error', True)
                
                print(f"\nAgent Execution Results:")
                print(f"  BehaviorTree Generated: {bt_generated}")
                print(f"  BehaviorTree Valid: {not bt_error}")
                print(f"  C# Compilation: {'OK' if not csharp_error else 'Errors'}")
                
                # Copy generated files and logs to output directory
                self._copy_generated_files(i, output_dir, result)
                self._copy_latest_log(output_dir, i)
                
                # Record summary
                run_summary = {
                    "run_number": i,
                    "bt_generated": bt_generated,
                    "bt_error": bt_error,
                    "csharp_error": csharp_error,
                    "success": bt_generated and not bt_error
                }
                results_summary.append(run_summary)
                
                if bt_generated and not bt_error:
                    print(f"✓ Run {i} completed successfully")
                else:
                    print(f"⚠ Run {i} completed with issues")
                
            except Exception as e:
                print(f"✗ Error in run {i}: {e}")
                traceback.print_exc()
                
                # Record failure in summary
                run_summary = {
                    "run_number": i,
                    "bt_generated": False,
                    "bt_error": True,
                    "csharp_error": True,
                    "success": False,
                    "error": str(e)
                }
                results_summary.append(run_summary)
                continue
        
        # Save results summary
        summary_path = output_dir / "results_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=2, ensure_ascii=False)
        
        # Print final summary
        print(f"\n{'='*60}")
        print("Experiment Completed!")
        print(f"{'='*60}")
        print(f"Results saved to: {output_dir}")
        
        successful_runs = sum(1 for r in results_summary if r.get('success', False))
        print(f"\nSuccess Rate: {successful_runs}/{num_repeats} ({100*successful_runs/num_repeats:.1f}%)")
        print(f"{'='*60}")
    
    def _copy_generated_files(self, run_number: int, output_dir: pathlib.Path, agent_result: dict):
        """
        Copy generated behavior tree files to the output directory
        
        Args:
            run_number: The run number being processed
            output_dir: Output directory for results
            agent_result: Result dict from run_agent execution
        """
        project_dir = pathlib.Path(os.getenv("PROJECT_DIRECTORY"))
        bt_dir = project_dir / "Assets" / "BehaviorTree"
        
        # Create run-specific subdirectory
        run_dir = output_dir / f"run_{run_number:02d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save run metadata with agent results
        metadata = {
            "run_number": run_number,
            "timestamp": datetime.now().isoformat(),
            "agent_result": {
                "bt_generated": agent_result.get('bt_generated', False),
                "bt_error": agent_result.get('bt_error', True),
                "csharp_error": agent_result.get('csharp_error', True),
            }
        }
        metadata_path = run_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Copy BehaviorTree.json if exists
        bt_json_path = bt_dir / "BehaviorTree.json"
        if bt_json_path.exists():
            output_json = run_dir / "BehaviorTree.json"
            shutil.copy2(bt_json_path, output_json)
            print(f"Copied BehaviorTree.json → run_{run_number:02d}/BehaviorTree.json")
        else:
            print("Warning: BehaviorTree.json not found")
        
        # Copy BehaviorTreePlan.txt if exists
        bt_plan_path = bt_dir / "BehaviorTreePlan.txt"
        if bt_plan_path.exists():
            output_plan = run_dir / "BehaviorTreePlan.txt"
            shutil.copy2(bt_plan_path, output_plan)
            print(f"Copied BehaviorTreePlan.txt → run_{run_number:02d}/BehaviorTreePlan.txt")
        
        # Copy all C# files in BehaviorTree directory if newnode is enabled
        if CONFIG.NEWNODE and bt_dir.exists():
            cs_files = list(bt_dir.rglob("*.cs"))
            if cs_files:
                cs_dir = run_dir / "CSharp"
                cs_dir.mkdir(parents=True, exist_ok=True)
                for cs_file in cs_files:
                    rel_path = cs_file.relative_to(bt_dir)
                    output_cs = cs_dir / rel_path
                    output_cs.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(cs_file, output_cs)
                print(f"Copied {len(cs_files)} C# files → run_{run_number:02d}/CSharp/")
    
    def _copy_latest_log(self, output_dir: pathlib.Path, run_number: int):
        """
        Copy the latest log file from editor/logs/ to the output directory
        
        Args:
            output_dir: Output directory for results
            run_number: Run number being processed
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
        
        # Copy to run subdirectory
        run_dir = output_dir / f"run_{run_number:02d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        dest_log = run_dir / f"agent_log.log"
        shutil.copy2(latest_log, dest_log)
        print(f"Copied log file → run_{run_number:02d}/agent_log.log")
    
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


def main():
    """Main entry point for running repeat experiments"""
    import argparse

    parser = argparse.ArgumentParser(description="Run repeat behavior tree generation experiment")
    parser.add_argument('--prompt', type=str, default="Create a strong Behavior Tree that it must win",
                       help='Prompt to repeat')
    parser.add_argument('--repeats', type=int, default=10,
                       help='Number of times to repeat (default: 10)')
    parser.add_argument('--newnode', action='store_true', default=False,
                       help='Allow C# node creation')
    parser.add_argument('--newbt', action='store_true', default=True,
                       help='(Reserved for future use)')
    parser.add_argument('--temperature', type=float, default=1.0,
                       help='LLM temperature setting (default: 1.0)')
    parser.add_argument('--model', type=str, default="gpt",
                       help='LLM model name or alias: gpt=gpt-5.2-2025-12-11, claude=claude-sonnet-4-6, gemini=gemini-2.5-pro')

    args = parser.parse_args()

    runner = RepeatExperimentRunner()
    runner.run_repeat_experiment(
        prompt=args.prompt,
        num_repeats=args.repeats,
        newnode=args.newnode,
        newbt=args.newbt,
        temperature=args.temperature,
        model=args.model,
    )


if __name__ == "__main__":
    main()
