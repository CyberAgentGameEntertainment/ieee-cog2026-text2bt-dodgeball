"""
Batch experiment runner for running multiple experiment configurations
"""
import argparse
import yaml
import pathlib
from typing import List, Dict, Any
from run_experiment import ExperimentRunner, ExperimentConfig


class BatchExperimentRunner:
    """Run multiple experiments based on configuration"""
    
    def __init__(self, config_path: pathlib.Path):
        """
        Initialize batch runner with configuration file
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.runner = ExperimentRunner()
    
    def run_all_experiments(self, dry_run: bool = False, model: str = None):
        """
        Run all experiments defined in configuration

        Args:
            dry_run: If True, only print what would be done
            model: LLM model override (None = use per-experiment yaml value or default)
        """
        experiments = self.config.get('experiments', [])

        print(f"Found {len(experiments)} experiment configurations")
        print()

        for i, exp_config in enumerate(experiments, 1):
            print(f"\n{'='*70}")
            print(f"Experiment {i}/{len(experiments)}: {exp_config['name']}")
            print(f"{'='*70}\n")

            resolved_model = model or exp_config.get('model', 'gpt')
            config = ExperimentConfig(
                level=exp_config['level'],
                newnode=exp_config['newnode'],
                newbt=exp_config['newbt'],
                temperature=exp_config.get('temperature', 1.0),
                num_repeats=exp_config.get('num_repeats', 1),
                model=resolved_model,
            )
            
            # Get task selection
            task_mode = self.config['experiment'].get('task_mode', 'all_tasks')
            task_numbers = None
            if task_mode == 'specific_tasks':
                task_numbers = self.config['experiment'].get('specific_tasks')
            
            # Run experiment
            self.runner.run_experiment(
                config=config,
                task_numbers=task_numbers,
                dry_run=dry_run
            )
            
            print(f"\nCompleted experiment: {exp_config['name']}")
    
    def run_single_experiment(self, name: str, dry_run: bool = False, model: str = None):
        """
        Run a single named experiment from configuration

        Args:
            name: Name of the experiment to run
            dry_run: If True, only print what would be done
            model: LLM model override (None = use per-experiment yaml value or default)
        """
        experiments = self.config.get('experiments', [])

        for exp_config in experiments:
            if exp_config['name'] == name:
                resolved_model = model or exp_config.get('model', 'gpt')
                config = ExperimentConfig(
                    level=exp_config['level'],
                    newnode=exp_config['newnode'],
                    newbt=exp_config['newbt'],
                    temperature=exp_config.get('temperature', 1.0),
                    num_repeats=exp_config.get('num_repeats', 1),
                    model=resolved_model,
                )
                
                # Get task selection
                task_mode = self.config['experiment'].get('task_mode', 'all_tasks')
                task_numbers = None
                if task_mode == 'specific_tasks':
                    task_numbers = self.config['experiment'].get('specific_tasks')
                
                self.runner.run_experiment(
                    config=config,
                    task_numbers=task_numbers,
                    dry_run=dry_run
                )
                return
        
        print(f"Error: Experiment '{name}' not found in configuration")
        print("Available experiments:")
        for exp in experiments:
            print(f"  - {exp['name']}")


def main():
    """Main entry point for batch experiment runner"""
    parser = argparse.ArgumentParser(
        description="Run batch behavior tree generation experiments"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--experiment',
        type=str,
        help='Name of specific experiment to run (runs all if not specified)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='LLM model override: gpt, claude, gemini, or full model ID (overrides yaml model field)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print what would be done without executing'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available experiments and exit'
    )
    
    args = parser.parse_args()
    
    # Get config path
    config_path = pathlib.Path(__file__).parent / args.config
    
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        return
    
    # Create batch runner
    batch_runner = BatchExperimentRunner(config_path)
    
    # List experiments if requested
    if args.list:
        experiments = batch_runner.config.get('experiments', [])
        print("Available experiments:")
        for exp in experiments:
            temp = exp.get('temperature', 1.0)
            repeats = exp.get('num_repeats', 1)
            model = exp.get('model', 'gpt')
            print(f"  - {exp['name']}")
            print(f"      Level: {exp['level']}, "
                  f"NEWNODE: {exp['newnode']}, "
                  f"NEWBT: {exp['newbt']}, "
                  f"Temperature: {temp}, "
                  f"Repeats: {repeats}, "
                  f"Model: {model}")
        return

    # Run experiments
    if args.experiment:
        batch_runner.run_single_experiment(args.experiment, dry_run=args.dry_run, model=args.model)
    else:
        batch_runner.run_all_experiments(dry_run=args.dry_run, model=args.model)


if __name__ == "__main__":
    main()
