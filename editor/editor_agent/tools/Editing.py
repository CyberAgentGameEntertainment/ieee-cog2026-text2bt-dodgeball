
import json
import pathlib
from dataclasses import asdict
from langchain.tools import tool
from editor_agent.Config import CONFIG
from editor_agent.Logging import LOGGER
from editor_agent.tools.UnityCompilation import fetch_unity_compile
from editor_agent.tools.BtDeserialization import fetch_bt_deserialization_result

@tool(description="This lists up all folders containing C# files in the project directory.")
def listup_folders_with_cs() -> list[str]:
    """
    Returns a list of directories containing C# files within
    """
    cs_folders = set()
    for path in (CONFIG.PROJECT_DIRECTORY / "Assets").rglob("*.cs"):
        cs_folders.add(str(path.parent.relative_to(CONFIG.PROJECT_DIRECTORY)))
    
    LOGGER.log(f"Listed C# folders: {cs_folders}")
    
    return list(cs_folders)

@tool(description="This lists up all C# files in the specified relative folder from the project directory.")
def listup_cs_files(relative_folder: str) -> list[str]:
    """
    Returns a list of C# files in the specified relative folder
    """
    folder_path = CONFIG.PROJECT_DIRECTORY / relative_folder
    cs_files = [str(path.name) for path in folder_path.glob("*.cs")]
    
    LOGGER.log(f"Listed C# files in {relative_folder}: {cs_files}")
    
    return cs_files

@tool(description="This returns the content of a file given its relative path from the project directory.")
def read_file(relative_path: str) -> str:
    """
    Reads the content of a file given its relative path from the project directory
    """
    file_path = CONFIG.PROJECT_DIRECTORY / relative_path

    if file_path.is_dir():
        LOGGER.log(f"Path is a directory, not a file: {relative_path}")
        return f"Error: '{relative_path}' is a directory, not a file. Use listup_cs_files to list its contents."

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        LOGGER.log(f"Read file {relative_path} with content length {len(content)}")

        return content
    except FileNotFoundError:
        LOGGER.log(f"File not found: {relative_path}")
        return f"Error: File not found - {relative_path}"

@tool(description="This searches for a keyword in all C# files in the specified relative folder and returns a list of file paths containing the keyword.")
def grep_cs_files(relative_folder: str, keyword: str) -> list[str]:
    """
    Searches for a keyword in all C# files in the specified relative folder
    and returns a list of file paths containing the keyword.
    """
    folder_path = CONFIG.PROJECT_DIRECTORY / relative_folder
    matching_files = []
    
    for path in folder_path.glob("*.cs"):
        with open(path, 'r', encoding='utf-8') as f:
            if keyword in f.read():
                matching_files.append(str(path.relative_to(CONFIG.PROJECT_DIRECTORY)))

    LOGGER.log(f"Found {len(matching_files)} files containing '{keyword}' in {relative_folder}")
    
    return matching_files

def _get_behavior_tree_directory(abs: bool = True) -> pathlib.Path:
    if abs:
        path = CONFIG.PROJECT_DIRECTORY / "Assets" / "BehaviorTree"
    else:
        path = pathlib.Path("Assets") / "BehaviorTree"

    # ensure directory existence
    path.mkdir(parents=True, exist_ok=True)

    return path

def _get_behavior_tree_plan_path(abs: bool = True) -> pathlib.Path:
    return _get_behavior_tree_directory(abs) / "BehaviorTreePlan.txt"

def _get_behavior_tree_json_path(abs: bool = True) ->pathlib.Path:
    return _get_behavior_tree_directory(abs) / "BehaviorTree.json"

@tool(description="This reads the behavior tree plan you created")
def read_behavior_tree_plan() -> str:
    """
    Reads the behavior tree plan from BehaviorTreePlan.txt in the project directory
    """
    plan_path = _get_behavior_tree_plan_path()
    if plan_path.exists():
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()

            LOGGER.log(f"Read behavior tree plan with content length {len(content)}")
            
            return content
    else:
        LOGGER.log("Behavior tree plan not found.")

        return "You have not created a behavior tree plan yet."

@tool(description="This writes the behavior tree plan to BehaviorTreePlan.txt in the project directory.")
def write_behavior_tree_plan(content: str) -> str:
    """
    Writes the behavior tree plan to BehaviorTreePlan.txt in the project directory
    """
    plan_path = _get_behavior_tree_plan_path()
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(content)

    LOGGER.log("Wrote behavior tree plan successfully.")

    return "Wrote behavior tree plan successfully."

@tool(description="This writes C# file to the specified relative path from the project directory. You can only write files within the Assets/BehaviorTree directory.")
def write_behavior_tree_cs_file(relative_path: str, content: str) -> str:
    """
    Writes C# code to the specified relative path from the project directory
    """
    abs_path = CONFIG.PROJECT_DIRECTORY / relative_path
    if not str(abs_path).startswith(str(_get_behavior_tree_directory())):
        LOGGER.log(f"Attempted to write outside BehaviorTree directory: {relative_path}")
        return "Error: You can only write files within the BehaviorTree directory. You need to write inside Assets/BehaviorTree/ directory."
    if not abs_path.suffix == ".cs":
        LOGGER.log(f"Attempted to write non-C# file: {relative_path}")
        return "Error: You can only write C# files with .cs extension."
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)

    LOGGER.log(f"Wrote file to {relative_path} successfully.")

    return f"Wrote file to {relative_path} successfully."

@tool(description="This writes behavior tree JSON to BehaviorTree.json in the BehaviorTree directory.")
def write_behavior_tree_json(content: str) -> str:
    """
    Writes behavior tree JSON to BehaviorTree.json in the BehaviorTree directory
    """
    json_path = _get_behavior_tree_json_path()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(content)

    LOGGER.log(f"Wrote behavior tree JSON successfully.: {len(content)} characters in {json_path}")

    return "Wrote behavior tree JSON successfully."

@tool(description="This reads the behavior tree JSON from BehaviorTree.json in the BehaviorTree directory.")
def read_behavior_tree_json() -> str:
    """
    Reads the behavior tree JSON from BehaviorTree.json in the BehaviorTree directory
    """
    json_path = _get_behavior_tree_json_path()
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()

            LOGGER.log(f"Read behavior tree JSON with content length {len(content)}")
            
            return content
    else:
        LOGGER.log("Behavior tree JSON not found.")

        return "Behavior tree JSON file not created yet"

@tool(description="This fetches the latest Unity compilation results. Don't finish editing until the result list is empty.")
def fetch_unity_compile_results() -> list[dict[str, str|int]]:
    """
    Fetches the latest Unity compilation results
    """
    compile_results = fetch_unity_compile()
    results_dicts = [asdict(result) for result in compile_results]
    LOGGER.log(f"Fetched compilation results: {results_dicts}")
    return results_dicts

@tool(description="This fetches the behavior tree deserialization result from Unity for the behavior tree JSON file path. Don't finish editing until the deserialization is successful.")
def fetch_bt_compile_result() -> str:
    """
    Fetches the behavior tree deserialization result from Unity for the specified behavior tree JSON file path
    """

    # check file existence
    rel_bt_path = _get_behavior_tree_json_path(abs=False)
    abs_bt_path = _get_behavior_tree_json_path(abs=True)
    if not abs_bt_path.exists():
        LOGGER.log(f"Behavior tree file not found: {rel_bt_path}")
        return f"Error: Behavior tree file is not created yet"

    result = fetch_bt_deserialization_result(rel_bt_path)
    LOGGER.log(f"Fetched behavior tree deserialization result for {rel_bt_path}: {result}")
    return result

LOGGER.bt_folder = _get_behavior_tree_directory()
