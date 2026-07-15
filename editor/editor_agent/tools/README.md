# Tools Documentation

This directory contains Python tools for the BehaviorTreeEditor agent. These tools enable the agent to interact with Unity projects, read/write files, and manage behavior trees.

## Overview

| Module | Description |
|--------|-------------|
| `BtDeserialization.py` | Fetches behavior tree deserialization results from Unity |
| `Editing.py` | Core editing tools for file operations and behavior tree management |
| `UnityCompilation.py` | Fetches Unity compilation status and error messages |

---

## BtDeserialization.py

Handles communication with Unity to deserialize behavior tree JSON files.

### `fetch_bt_deserialization_result(bt_path: str) -> str`

Fetches the behavior tree deserialization result from Unity via socket communication.

**Parameters:**
- `bt_path` (str): Path to the behavior tree JSON file (e.g., `"Assets/BehaviorTree/PlayerDodgeballBT.json"`)

**Returns:**
- `str`: The deserialization result from Unity

**Raises:**
- `ConnectionError`: If connection to Unity fails after 5 retry attempts

**Configuration:**
- Connects to `localhost:5001`

---

## Editing.py

Contains the main editing tools exposed to the LangChain agent for file operations and behavior tree management.

### `listup_folders_with_cs() -> list[str]`

Lists all folders containing C# files in the project directory.

**Returns:**
- `list[str]`: List of directory paths relative to the project directory

---

### `listup_cs_files(relative_folder: str) -> list[str]`

Lists all C# files in the specified folder.

**Parameters:**
- `relative_folder` (str): Folder path relative to the project directory

**Returns:**
- `list[str]`: List of C# file names in the specified folder

---

### `read_file(relative_path: str) -> str`

Reads the content of a file.

**Parameters:**
- `relative_path` (str): File path relative to the project directory

**Returns:**
- `str`: File content, or an error message if the file is not found

---

### `grep_cs_files(relative_folder: str, keyword: str) -> list[str]`

Searches for a keyword in all C# files in a folder.

**Parameters:**
- `relative_folder` (str): Folder path relative to the project directory
- `keyword` (str): The keyword to search for

**Returns:**
- `list[str]`: List of file paths containing the keyword

---

### `read_behavior_tree_plan() -> str`

Reads the behavior tree plan from `BehaviorTreePlan.txt`.

**Returns:**
- `str`: Content of the behavior tree plan, or a message indicating no plan exists

---

### `write_behavior_tree_plan(content: str) -> str`

Writes the behavior tree plan to `BehaviorTreePlan.txt`.

**Parameters:**
- `content` (str): The plan content to write

**Returns:**
- `str`: Success message

---

### `write_behavior_tree_file(relative_path: str, content: str) -> str`

Writes a file to the specified path. The function validates at runtime that the resolved absolute path is within the `Assets/BehaviorTree` directory.

**Parameters:**
- `relative_path` (str): File path relative to the project directory (function will validate the resolved path is within `Assets/BehaviorTree/` directory)
- `content` (str): The content to write

**Returns:**
- `str`: Success message, or an error if the resolved path is outside the allowed directory

**Security:**
- Only allows writing files within `Assets/BehaviorTree/` directory

---

### `fetch_unity_compile_results() -> list[dict[str, str|int]]`

Fetches the latest Unity compilation results.

**Returns:**
- `list[dict[str, str|int]]`: List of compilation results, each containing:
  - `message` (str): The compilation error/warning message
  - `filename` (str): Name of the file with the issue
  - `line_raw` (str): The source code line causing the issue
  - `line` (int): Line number of the issue

---

### `fetch_bt_compile_result(bt_path: str) -> str`

Fetches behavior tree deserialization result for a specific JSON file.

**Parameters:**
- `bt_path` (str): Path to the behavior tree JSON file

**Returns:**
- `str`: Deserialization result, or an error message if the file is not found

---

## UnityCompilation.py

Handles communication with Unity to fetch compilation status.

### Data Classes

#### `UnityCompileResultRaw`
Raw compilation result from Unity.
- `type` (str): Type of the message
- `message` (str): The compilation message
- `file` (str): Full file path
- `line` (int): Line number
- `column` (int): Column number

#### `UnityCompileResult`
Processed compilation result.
- `message` (str): The compilation message
- `filename` (str): File name only
- `line_raw` (str): The source code line
- `line` (int): Line number

### `fetch_unity_compile() -> list[UnityCompileResult]`

Fetches and processes Unity compilation status.

**Returns:**
- `list[UnityCompileResult]`: List of processed compilation results

**Raises:**
- `ConnectionError`: If connection to Unity fails after 5 retry attempts

**Configuration:**
- Connects to `localhost:5000`

---

## Configuration

The tools use configuration from `editor_agent.Config`:
- `CONFIG.PROJECT_DIRECTORY`: The root directory of the Unity project being edited. This is loaded from the `PROJECT_DIRECTORY` environment variable, which should be set in a `.env` file at the repository root.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PROJECT_DIRECTORY` | Absolute path to the Unity project directory |

## Logging

All tools log their operations using `editor_agent.Logging.LOGGER`.
