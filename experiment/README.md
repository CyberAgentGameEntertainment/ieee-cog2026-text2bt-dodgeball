# Experiment Framework

This directory contains tools for running experiments to generate behavior trees using the editor agent.

## Structure

```
experiment/
├── tasks.json             # Task definitions (converted from raw.md)
├── run_experiment.py      # Main experiment runner
├── batch_run.py          # Batch experiment runner
├── config.yaml           # Configuration file for experiments
└── results/              # Generated behavior tree results
    ├── 20260123120000_1_no-newnode_newbt/   # Timestamped results
    │   ├── task_01/
    │   ├── task_02/
    │   └── ...
    ├── 20260123130000_2_no-newnode_newbt/
    └── ...
```

## Usage

### Quick Start

Run with default settings (Level 1, newnode=false, newbt=true):

```bash
cd experiment
uv run python run_experiment.py
```

Expected output:
```
=== Experiment Configuration ===
Level: 1
NEWNODE: False
NEWBT: True
Output Directory: C:\...\results\20260123120000_1_no-newnode_newbt
Number of Tasks: 9
Dry Run: False

============================================================
Processing Task 1: Idle Spinner
============================================================

Prompt:
* Start rotating 90 degrees per second

Running editor agent...

Agent Execution Results:
  BehaviorTree Generated: True
  BehaviorTree Valid: True
  C# Compilation: OK

✓ Task 1 completed successfully
```

With specific options:

```bash
# Run specific tasks
uv run python run_experiment.py --tasks 1 2 3

# Use level 2 prompts
uv run python run_experiment.py --level 2

# Allow C# node creation
uv run python run_experiment.py --newnode true

# Set temperature to 1.0 (default)
uv run python run_experiment.py --temperature 1.0

# Repeat each task 10 times
uv run python run_experiment.py --repeats 10

# Combine multiple options
uv run python run_experiment.py --level 1 --temperature 1.0 --repeats 10

# Dry run
uv run python run_experiment.py --dry-run
```

### Strongest Experiment

Run experiments using prompts from `Strongest.md` (10 adversarial prompts designed to create unbeatable agents):

**Note:** Both `--newnode` and `--newbt` are required arguments and must be explicitly set to `true` or `false`.

```bash
# Run all 10 prompts once (newnode disabled, newbt enabled)
uv run python run_strongest_experiment.py --newnode false --newbt true --repeats 1

# Run with new node creation enabled, temperature 0.7, 5 repeats
uv run python run_strongest_experiment.py --newnode true --newbt true --temperature 0.7 --repeats 5

# Run only specific prompts (e.g., prompts 1, 5, and 10)
uv run python run_strongest_experiment.py --newnode false --newbt true --prompts 1 5 10

# Dry run to see what would happen without executing
uv run python run_strongest_experiment.py --newnode false --newbt true --dry-run

# Full configuration example (10 repeats with new nodes)
uv run python run_strongest_experiment.py --newnode true --newbt true --temperature 1.0 --repeats 10
```

Expected output:
```
=== Strongest Experiment Configuration ===
NEWNODE: False
NEWBT: True
Temperature: 1.0
Number of Repeats: 1
Output Directory: C:\...\results\20260209120000_strongest_...
Number of Prompts: 10
Dry Run: False

============================================================
Prompt 1/10: Create a powerful player that never loses...
============================================================

Running agent with prompt: Create a powerful player that never loses...

Agent completed:
  - BT Generated: True
  - BT Error: False
  - C# Error: False

Copied BehaviorTree.json → prompt_01/BehaviorTree.json
Copied BehaviorTreePlan.txt → prompt_01/BehaviorTreePlan.txt
Copied log file → prompt_01/agent_log.log
```

### Batch Experiments

List available experiments:

```bash
uv run python batch_run.py --list
```

Output:
```
Available experiments:
  - level1_no_newnode      (Level: 1, NEWNODE: False, NEWBT: True, Temperature: 1.0, Repeats: 1)
  - level1_with_newnode    (Level: 1, NEWNODE: True, NEWBT: True, Temperature: 1.0, Repeats: 1)
  - level2_no_newnode      (Level: 2, NEWNODE: False, NEWBT: True, Temperature: 1.0, Repeats: 1)
  - level2_with_newnode    (Level: 2, NEWNODE: True, NEWBT: True, Temperature: 1.0, Repeats: 1)
  - level1_no_newnode_repeat10  (Level: 1, NEWNODE: False, NEWBT: True, Temperature: 1.0, Repeats: 10)
```

Run a specific experiment by name:

```bash
# Level 1 without custom nodes
uv run python batch_run.py --experiment level1_no_newnode

# Level 2 without custom nodes
uv run python batch_run.py --experiment level2_no_newnode

# Level 1 with custom nodes
uv run python batch_run.py --experiment level1_with_newnode

# Level 2 with custom nodes
uv run python batch_run.py --experiment level2_with_newnode

# Level 1 with 10 repeats per task
uv run python batch_run.py --experiment level1_no_newnode_repeat10
```

Run all experiments defined in `config.yaml`:

```bash
uv run python batch_run.py
```

Dry run (see what would be executed without running):

```bash
uv run python batch_run.py --experiment level2_no_newnode --dry-run
```

### Custom Configuration

Edit `run_experiment.py` to customize the experiment:

```python
config = Exper,     # (Reserved for future use)
    temperature=1.0,  # LLM temperature (default: 1.0)
    num_repeats=10   # Number of times to repeat each task
    level=1,        # 1 or 2 (prompt level from raw.md)
    newnode=False,  # Allow C# node creation
    newbt=True      # (Reserved for future use)
)

# Run for all tasks
runner.run_experiment(config=config)

# Or run for specific tasks only
runner.run_experiment(config=config, task_numbers=[1, 2, 3])

# Or dry run to see what would be executed
runner.run_experiment(config=config, dry_run=True)
```

### Programmatic Usage

```python
from run_experiment import ExperimentRunner, ExperimentConfig

runner = ExperimentRunner()
, temperature=1.0, num_repeats=1)
runner.run_experiment(config_1)

# Level 2 with new nodes allowed, temperature 1.0, repeated 10 times
config_2 = ExperimentConfig(level=2, newnode=True, newbt=True, temperature=1.0, num_repeats=10
# Level 2 with new nodes allowed
config_2 = ExperimentConfig(level=2, newnode=True, newbt=True)
runner.run_experiment(config_2)
```

### Collect BehaviorTree.json Files

Gather all `BehaviorTree.json` files from a strongest experiment result directory into a single flat folder:

```bash
# Default output: <result_dir>/collected_behavior_trees/
uv run python collect_behavior_trees.py results/20260512162941_strongest_newnodeFalse_newbtTrue_temp1.0_rep10_claude

# Specify output directory
uv run python collect_behavior_trees.py results/20260512162941_strongest_newnodeFalse_newbtTrue_temp1.0_rep10_claude --output path/to/output_dir
```

Output filenames follow the pattern `<subfolder>_BehaviorTree.json`:

```
collected_behavior_trees/
├── prompt_01_BehaviorTree.json
├── prompt_01_repeat_2_BehaviorTree.json
├── ...
├── prompt_10_repeat_9_BehaviorTree.json
└── prompt_10_repeat_10_BehaviorTree.json
```

## Task Data

Tasks are stored in [tasks.json](tasks.json) with the following structure:

```json
{
  "tasks": [
    {
      "task_number": 1,
      "name": "Idle Spinner",
      "description": "Task description...",
      "level1_prompt": "Level 1 prompt...",
      "level2_prompt": "Level 2 prompt..."
    }
  ]
}
```

To update tasks, edit `tasks.json` directly.

## Output

Generated files are saved to `results/YYYYMMDDHHMMSS_{level}_{newnode}_{newbt}_temp{temperature}/` with the following structure:

```
results/
└── 20260123120000_1_no-newnode_newbt_temp1.0/
    ├── task_01/
    │   ├── metadata.json           # Task metadata and timestamp
    │   ├── BehaviorTree.json       # Generated behavior tree
    │   ├── BehaviorTreePlan.txt    # Natural language plan
    │   ├── agent_log.log           # Editor agent execution log
    │   └── CSharp/                 # C# files (if newnode=true)
    │       └── *.cs
    ├── task_01_repeat02/           # Second repeat of task 1
    │   └── ...
    ├── task_02/
    │   └── ...
    └── ...
```

### Result Files

- **metadata.json**: Contains task information, generation timestamp, and agent execution results:
  ```json
  {
    "task_number": 1,
    "name": "Idle Spinner",
    "description": "...",
    "timestamp": "2026-01-23T12:00:00",
    "agent_result": {
      "bt_generated": true,
      "bt_error": false,
      "csharp_error": false
    }
  }
  ```
- **BehaviorTree.json**: The generated behavior tree in JSON format
- **BehaviorTreePlan.txt**: Natural language description of the behavior tree
- **agent_log.log**: Complete log of the editor agent's execution process
- **CSharp/**: C# node implementations (only when newnode=true)

### Unity Project Reset

After each task completion:
1. Generated files are copied to the results directory
2. Unity project's `Assets/BehaviorTree/` directory is reset using git
3. All changes (staged, unstaged, and untracked files) are removed
4. The project is ready for the next task

## Configuration Options

### ExperimentConfig

- **level** (int): Which prompt level to use from raw.md (1 or 2)
  - Level 1: More structured, formal BT syntax
  - Level 2: Natural language description
  
- **newnode** (bool): Whether to allow C# node creation
  - `true`: Agent can create new C# behavior tree nodes
  - `false`: Agent must use only existing nodes

- **temperature** (float): LLM temperature setting (default: 1.0)
  - Controls randomness in LLM responses
  - Higher values (e.g., 1.0) produce more creative/varied outputs
  - Lower values (e.g., 0.0) produce more deterministic outputs

- **num_repeats** (int): Number of times to repeat each task (default: 1)
  - Useful for testing consistency and variance of generated behavior trees
  - Each repeat creates a separate output directory (e.g., `task_01_repeat02`)
  - Temperature > 0 with multiple repeats will produce different results each time
  
- **newbt** (bool): Reserved for future behavior tree options

## Requirements

- The editor module must be properly configured with `.env` file
- Unity project path must be set in the editor's `.env` file
- All dependencies from the editor module must be installed
- Editor uses LangGraph-based agent architecture for behavior tree generation

## Architecture

The experiment framework integrates with the editor's LangGraph-based agent system:

1. **Agent Graph**: The editor uses a state-based graph architecture (LangGraph)
2. **State Tracking**: Each agent execution tracks:
   - `bt_generated`: Whether BehaviorTree.json was created
   - `bt_error`: Whether there are BT deserialization errors
   - `csharp_error`: Whether there are C# compilation errors
3. **Result Metadata**: All execution results are saved in metadata.json for analysis
