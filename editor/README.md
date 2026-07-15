## BEFORE RUNNING
<img width="482" height="691" alt="Image" src="https://github.com/user-attachments/assets/929c195d-54a0-48e3-87ea-4f5dbc6cb213" />

## Running

```
uv run -m editor_agent.Agent
```

## Configuration

Create a `.env` file based on `template.env`:

```dotenv
OPENAI_API_KEY=your-api-key
PROJECT_DIRECTORY=/path/to/unity/project
NEWNODE=true  # true: Allow C# node creation, false: Use only existing nodes
NEWBT=true    # (Reserved for future use)
```

### Options

- **NEWNODE**: Controls whether the agent can create new C# behavior tree nodes
  - `true` (default): Agent can implement new C# nodes for behavior tree
  - `false`: Agent can only use existing nodes, no C# programming allowed

- **NEWBT**: Reserved for future behavior tree related features
  - Currently a placeholder option
