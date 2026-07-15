"""
Convert raw.md task descriptions to tasks.json format
"""
import json
import pathlib
import re
import random
from itertools import permutations
from typing import List, Dict


def generate_line_permutations(text: str, max_permutations: int = 4) -> List[str]:
    """
    Generate random permutations of lines in text.
    
    Args:
        text: The text to permute (lines separated by newlines)
        max_permutations: Maximum number of permutations to generate
        
    Returns:
        List of permuted text strings (all unique)
    """
    lines = text.split('\n')
    
    # Calculate maximum possible permutations
    import math
    num_lines = len(lines)
    max_possible = math.factorial(num_lines)
    
    # Limit to the smaller of max_permutations or max_possible
    target_count = min(max_permutations, max_possible)
    
    if num_lines <= 1:
        # Single line - only one permutation possible
        return [text]
    
    # Generate all permutations and randomly sample
    all_perms = list(permutations(lines))
    
    # Randomly sample unique permutations
    selected_perms = random.sample(all_perms, target_count)
    
    # Join lines back together
    result = ['\n'.join(perm) for perm in selected_perms]
    
    return result


def parse_raw_md(md_content: str) -> List[Dict[str, str]]:
    """
    Parse the raw.md markdown file and extract task information.
    
    Args:
        md_content: The content of raw.md file
        
    Returns:
        List of task dictionaries with name, description, level1_prompt, level2_prompt
    """
    tasks = []
    
    # Split by task headers - supports both formats:
    # ## **Task X: ...** and ## Task X: ...
    task_pattern = r'## (?:\*\*)?Task \d+: (.+?)(?:\*\*)?(?=\n|$)'
    task_sections = re.split(task_pattern, md_content)
    
    # First element is the header, skip it
    # Then we have alternating: task_name, task_content, task_name, task_content, ...
    for i in range(1, len(task_sections), 2):
        if i + 1 >= len(task_sections):
            break
            
        task_name = task_sections[i].strip()
        task_content = task_sections[i + 1].strip()
      
        # Extract Level 1 prompt - supports both "Level 1:" and "Level1:"
        level1_match = re.search(r'Level\s*1:\s*```\s*(.+?)\s*```', task_content, re.DOTALL)
        level1_prompt = level1_match.group(1).strip() if level1_match else ""
        
        # Extract Level 2 prompt - supports both "Level 2:" and "Level2:"
        level2_match = re.search(r'Level\s*2:\s*```\s*(.+?)\s*```', task_content, re.DOTALL)
        level2_prompt = level2_match.group(1).strip() if level2_match else ""
        
        # Generate 4 random permutations of level2 lines
        level2_variations = generate_line_permutations(level2_prompt, max_permutations=4)
        
        task = {
            "name": task_name,
            "level1_prompt": level1_prompt,
            "level2_prompt": level2_variations  # Now a list
        }
        
        tasks.append(task)
    
    return tasks


def convert_raw_to_json(raw_md_path: pathlib.Path, output_json_path: pathlib.Path):
    """
    Convert raw.md to tasks.json format.
    
    Args:
        raw_md_path: Path to the raw.md file
        output_json_path: Path where tasks.json should be saved
    """
    # Read raw.md
    try:
        with open(raw_md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"Error: {raw_md_path} not found!")
        return
    except Exception as e:
        print(f"Error reading {raw_md_path}: {e}")
        return
    
    # Parse tasks
    print("Parsing tasks from raw.md...")
    tasks = parse_raw_md(md_content)
    print(f"Found {len(tasks)} tasks")
    
    # Create JSON structure
    json_data = {
        "tasks": tasks
    }
    
    # Save to JSON file
    try:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Successfully converted to {output_json_path}")
        print(f"  Total tasks: {len(tasks)}")
        
        # Show preview of first task
        if tasks:
            print("\nPreview of first task:")
            print(f"  Name: {tasks[0]['name']}")
            
    except Exception as e:
        print(f"\n✗ Error saving JSON file: {e}")


def main():
    """Main entry point"""
    # Setup paths
    base_dir = pathlib.Path(__file__).parent
    docs_dir = base_dir.parent / "docs" / "tasks"
    
    raw_md_path = docs_dir / "raw.md"
    output_json_path = base_dir / "tasks.json"
    
    print("=" * 60)
    print("Raw.md to Tasks.json Converter")
    print("=" * 60)
    print(f"Input:  {raw_md_path}")
    print(f"Output: {output_json_path}")
    print("=" * 60)
    
    # Check if output file exists
    if output_json_path.exists():
        print(f"\nWarning: {output_json_path} already exists!")
        confirm = input("Overwrite? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Cancelled.")
            return
    
    # Convert
    convert_raw_to_json(raw_md_path, output_json_path)


if __name__ == "__main__":
    main()
