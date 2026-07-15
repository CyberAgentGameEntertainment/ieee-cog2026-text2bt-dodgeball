"""
CLI tool to add tasks to tasks.json
"""
import json
import pathlib
import sys


def read_multiline_input(prompt: str) -> str:
    """
    Read multiple lines of input. User can paste text with newlines.
    Input ends when user enters 'END' on a line by itself.
    
    Args:
        prompt: The prompt to display to the user
        
    Returns:
        The multiline text entered by the user
    """
    print(f"\n{prompt}")
    print("(Enter 'END' on a line by itself to finish, or Ctrl+Z then Enter on Windows / Ctrl+D on Unix)")
    print("-" * 60)
    
    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
    except EOFError:
        # Ctrl+D (Unix) or Ctrl+Z (Windows) was pressed
        pass
    
    return '\n'.join(lines)


def add_single_task(tasks_json_path: pathlib.Path) -> bool:
    """
    Add a single task to tasks.json
    
    Args:
        tasks_json_path: Path to tasks.json file
        
    Returns:
        True if task was added, False if cancelled
    """
    # Load existing tasks (reload each time to get latest state)
    try:
        with open(tasks_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {tasks_json_path} not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {tasks_json_path}: {e}")
        sys.exit(1)
    
    print("=" * 60)
    print("Add New Task")
    print("=" * 60)
    
    # Get task information
    print("\nTask Name:")
    name = input("> ").strip()
    
    print("\nTask Description:")
    description = input("> ").strip()
    
    level1_prompt = read_multiline_input("Level 1 Prompt (structured format):")
    level2_prompt = read_multiline_input("Level 2 Prompt (natural language format):")
    
    # Create new task object (without task_number - it will be auto-assigned)
    new_task = {
        "name": name,
        "description": description,
        "level1_prompt": level1_prompt,
        "level2_prompt": level2_prompt
    }
    
    # Show preview
    print("\n" + "=" * 60)
    print("Preview of new task:")
    print("=" * 60)
    print(f"Name: {name}")
    print(f"Description: {description}")
    print(f"Level 1 Prompt:\n{level1_prompt}")
    print(f"Level 2 Prompt:\n{level2_prompt}")
    print("=" * 60)
    
    # Confirm
    confirm = input("\nAdd this task? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Skipped.")
        return False
    
    # Add to tasks list
    data['tasks'].append(new_task)
    
    # Save to file immediately (in case of Ctrl+C later)
    try:
        with open(tasks_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Task added successfully!")
        print(f"Task will be assigned number {len(data['tasks'])} automatically")
        return True
    except Exception as e:
        print(f"\n✗ Error saving file: {e}")
        sys.exit(1)


def add_task_interactive():
    """
    Interactively add tasks to tasks.json (repeatable)
    """
    # Get the tasks.json path
    base_dir = pathlib.Path(__file__).parent
    tasks_json_path = base_dir / "tasks.json"
    
    print("\n" + "=" * 60)
    print("Task Addition Tool - Press Ctrl+C anytime to exit")
    print("=" * 60)
    
    added_count = 0
    
    while True:
        try:
            if add_single_task(tasks_json_path):
                added_count += 1
            
            # Ask if user wants to add another
            print("\n" + "-" * 60)
            another = input("Add another task? (yes/no): ").strip().lower()
            if another not in ['yes', 'y']:
                break
            print()
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            break
    
    print(f"\n{'=' * 60}")
    print(f"Total tasks added: {added_count}")
    print(f"{'=' * 60}")


def main():
    """Main entry point"""
    add_task_interactive()


if __name__ == "__main__":
    main()
