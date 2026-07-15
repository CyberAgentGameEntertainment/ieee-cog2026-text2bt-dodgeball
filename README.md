# Text2BT: LLM-Agent-Based Behavior-Tree Generation for Game Character AI

This repository accompanies the paper:

> **Text2BT: A Baseline Study on LLM-Agent-Based Behavior-Tree Generation for
> Game Character AI**
> _Submitted to IEEE Conference on Games (CoG) 2026._

Text2BT is an LLM-agent pipeline that turns a natural-language instruction into a
runnable **behavior tree (BT)** for a game character. The generated trees drive
agents in a Unity **DodgeBall** environment, and this repository contains the
agent, the experiment automation used for the paper, and the analysis code
behind the reported results.

---

## Repository structure

| Directory                                                              | Contents                                                                                                                                                                  |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`editor/`](editor/)                                                   | The BT-generation **agent** (LangGraph-based). Takes a natural-language prompt and produces a `BehaviorTree.json` (and optionally new C# nodes) inside the Unity project. |
| [`experiment/`](experiment/)                                           | **Experiment automation** used for the paper: runners that invoke the editor agent over the task sets, reset the Unity project between runs, and collect results.         |
| [`ml-agents-dodgeball-env-develop/`](ml-agents-dodgeball-env-develop/) | The **Unity DodgeBall environment** (vendored from Unity ML-Agents; Apache 2.0) that executes the generated behavior trees.                                               |
| [`docs/tasks/`](docs/tasks/)                                           | Task definitions and node reference: `raw.md` (task prompts), `nodes.md` (available BT nodes), `Strongest.md` (adversarial prompts), `manualcheck.md`.                    |
| [`writing/`](writing/)                                                 | **Paper-writing artifacts**: the LaTeX source, figures, result CSVs, and the win-rate analysis/plotting scripts.                                                          |

---

## Requirements

- **Python ≥ 3.12**, with [uv](https://github.com/astral-sh/uv) for dependency
  and environment management.
- **Unity Editor 2020.2.6 or later** (to open and run the DodgeBall environment
  and to compile any newly generated C# nodes).
- **Git** (the experiment runners reset the Unity project's `Assets/BehaviorTree/`
  between runs).
- **At least one LLM API key**, depending on the model you run:
  - OpenAI (`OPENAI_API_KEY`) for `gpt`
  - Anthropic (`CLAUDE_API_KEY`) for `claude`
  - Google (`GEMINI_API_KEY`) for `gemini`

---

## Setup

1. **Clone the repository.**

2. **Configure the agent.** The agent and experiment runners read configuration
   from `editor/.env`. Create it from the template:

   ```bash
   cp editor/template.env editor/.env
   ```

   Then fill in the values:

   ```dotenv
   OPENAI_API_KEY=your-openai-key      # required for --model gpt
   CLAUDE_API_KEY=your-anthropic-key   # required for --model claude
   GEMINI_API_KEY=your-google-key      # required for --model gemini
   PROJECT_DIRECTORY=/absolute/path/to/ml-agents-dodgeball-env-develop
   NEWNODE=true    # allow the agent to author new C# BT nodes
   NEWBT=true      # (reserved)
   MODEL=gpt       # default model alias when not overridden on the CLI
   ```

   `PROJECT_DIRECTORY` must point at the Unity project (the
   `ml-agents-dodgeball-env-develop/` directory in this repository, or your own
   checkout of it). Generated behavior trees are written to
   `<PROJECT_DIRECTORY>/Assets/BehaviorTree/`.

3. **Open the Unity project** (`ml-agents-dodgeball-env-develop/`) in the Unity
   Editor so that generated trees and C# nodes can be compiled and run.

Dependencies are installed automatically on first `uv run` in each directory.

### Model aliases

The `--model` flag (and the `MODEL` env var) accept short aliases, resolved in
`editor/editor_agent/graph/GraphNodes.py`:

| Alias    | Resolved model       | API key          |
| -------- | -------------------- | ---------------- |
| `gpt`    | `gpt-5.2-2025-12-11` | `OPENAI_API_KEY` |
| `claude` | `claude-sonnet-4-6`  | `CLAUDE_API_KEY` |
| `gemini` | `gemini-2.5-pro`     | `GEMINI_API_KEY` |

A full model name may also be passed directly; the provider is inferred from its
prefix (`claude-*` → Anthropic, `gemini-*` → Google, otherwise OpenAI).

---

## Running the agent directly

To generate a single behavior tree interactively from the editor agent:

```bash
cd editor
uv run -m editor_agent.Agent
```

See [`editor/README.md`](editor/README.md) for details.

---

## Reproducing BT generation (paper experiments)

All experiments are launched from the `experiment/` directory. Each run invokes
the editor agent once per task/prompt (× repeats), resets the Unity project
between runs, and writes results to `experiment/results/<timestamp>_<config>/`.

Set `{MODEL}` to `gpt` or `claude` to reproduce each of the two model conditions
reported in the paper.

```bash
cd experiment
```

**Experiment 1** — task set, Level 1 prompts:

```bash
uv run python run_experiment.py --level 1 --newnode false --newbt true --temperature 1.0 --repeats 10 --model {MODEL}
```

**Experiment 2** — task set, Level 2 prompts:

```bash
uv run python run_experiment.py --level 2 --newnode false --newbt true --temperature 1.0 --repeats 10 --model {MODEL}
```

**Experiment 3** — "Strongest" adversarial prompt set:

```bash
uv run python run_strongest_experiment.py --newnode false --newbt true --temperature 1.0 --repeats 10 --model {MODEL}
```

Run each of the three commands twice, once with `--model gpt` and once with
`--model claude`, to reproduce both model conditions.

### Common flags

| Flag                                | Meaning                                                                               |
| ----------------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `--level {1,2}`                     | Prompt level from the task set (`run_experiment.py` only).                            |
| `--newnode {true,false}`            | Whether the agent may author new C# BT nodes. `false` restricts it to existing nodes. |
| `--newbt {true,false}`              | Reserved flag (kept for configuration completeness).                                  |
| `--temperature <float>`             | LLM sampling temperature (paper uses `1.0`).                                          |
| `--repeats <int>`                   | Repeats per task/prompt (paper uses `10`).                                            |
| `--model <alias                     | name>`                                                                                | `gpt`, `claude`, `gemini`, or an explicit model name. |
| `--tasks N ...` / `--prompts N ...` | Restrict to specific task/prompt numbers.                                             |
| `--dry-run`                         | Print what would run without executing.                                               |

For the full experiment-framework reference (output layout, batch runs,
result-collection utilities, isomorphism analysis), see
[`experiment/README.md`](experiment/README.md).

### Output

Results are written under `experiment/results/` with per-task/per-prompt
subfolders, each containing `metadata.json`, the generated `BehaviorTree.json`,
`BehaviorTreePlan.txt`, the agent log, and any generated C# (when
`--newnode true`).

---

## Analysis and figures

The win-rate analysis and figures in the paper are produced from the collected
match data under [`writing/data/`](writing/data/):

```bash
cd writing
uv run python winrates_hist.py            # win-rate histogram
uv run python winrates_hist_compare.py    # comparison across conditions
```

Statistical exploration lives in `writing/winrates_test.ipynb`, and the LaTeX
source of the paper is under
[`writing/llm_bt_IEEECoG2026_short/`](writing/llm_bt_IEEECoG2026_short/).

---

## License

- This repository's own code and documentation (`editor/`, `experiment/`,
  `writing/`, and the top-level docs) are released under the **MIT License** —
  see [LICENSE](LICENSE).
- The bundled Unity DodgeBall environment in
  `ml-agents-dodgeball-env-develop/` is © Unity Technologies and licensed under
  the **Apache License 2.0**; it is **not** covered by the MIT License above.
- A full inventory of bundled components, Python dependencies, and external
  services, together with their licenses, is in
  [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Citation

If you use this code, please cite the paper:

```bibtex
@inproceedings{text2bt2026,
  title     = {Text2BT: A Baseline Study on LLM-Agent-Based Behavior-Tree
               Generation for Game Character AI},
  author    = {Ito, Ray and Jimbo, Naoyuki and Ihara, Koya}
  booktitle = {Proceedings of the IEEE Conference on Games (CoG)},
  year      = {2026}
}
```
