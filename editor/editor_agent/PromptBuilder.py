import pathlib
from editor_agent.Config import CONFIG


class PromptBuilder:
    """Class to dynamically construct prompts"""

    def __init__(self):
        self.prompts_dir = pathlib.Path(__file__).parent / "prompts"

    def build_system_prompt(self) -> str:
        """
        Construct the system prompt based on the configuration

        Returns:
            str: The constructed system prompt
        """
        sections = []
        
        # 1. Requirement section
        sections.append(self._read_prompt_file("Requirement.txt"))
        
        # 2. Add step for C# implementation if newnode is enabled
        if CONFIG.NEWNODE:
            sections.append(self._read_prompt_file("Step_CSharpImplementation.txt"))
        
        # 3. Add step for JSON implementation (always included)
        sections.append(self._read_prompt_file("Step_JsonImplementation.txt"))
        
        # 4. Add JSON specification
        sections.append("\n## JSON Specification\n")
        sections.append(self._read_prompt_file("JSON_Specification.md"))
        
        # 5. Base constraints
        sections.append(self._read_prompt_file("Constraints_Base.txt"))
        
        # 6. Add C# constraints if newnode is enabled
        if CONFIG.NEWNODE:
            sections.append(self._read_prompt_file("Constraints_CSharp.txt"))
        else:
            # Add note that C# programming is not allowed
            sections.append(self._get_no_csharp_constraint())
        
        # Join all sections
        return "\n".join(sections)

    def _read_prompt_file(self, filename: str) -> str:
        """Read a prompt file"""
        filepath = self.prompts_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def _get_no_csharp_constraint(self) -> str:
        """
        Get the constraint text for when C# programming is not allowed
        
        Returns:
            str: The constraint text
        """
        return "- You are NOT allowed to write or modify any C# code. Use only existing nodes written by C# for behavior tree implementation."


# Global instance
PROMPT_BUILDER = PromptBuilder()
