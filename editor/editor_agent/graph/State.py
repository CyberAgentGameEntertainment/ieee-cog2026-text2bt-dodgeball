"""
State definition for the agent graph.
"""

import pathlib
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from editor_agent.Config import CONFIG


class AgentGraphState(TypedDict):
    """State for the agent graph with additional compilation status tracking.
    
    Attributes:
        messages: Chat history with the agent (automatically merged via add_messages).
        csharp_error: True if there are C# compilation errors.
        bt_generated: True if BehaviorTree.json has been generated.
        bt_error: True if there are BT deserialization errors.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    csharp_error: bool
    bt_generated: bool
    bt_error: bool


def check_bt_json_exists() -> bool:
    """Check if BehaviorTree.json exists in the project.
    
    Returns:
        bool: True if the BehaviorTree.json file exists.
    """
    bt_path = CONFIG.PROJECT_DIRECTORY / "Assets" / "BehaviorTree" / "BehaviorTree.json"
    return bt_path.exists()


def create_initial_state(user_input: str) -> dict:
    """Create the initial state for the agent graph.
    
    Args:
        user_input: The user's request/query.
        
    Returns:
        dict: Initial state dictionary with default values.
    """
    from langchain_core.messages import HumanMessage
    
    return {
        "messages": [HumanMessage(content=user_input)],
        "csharp_error": True,
        "bt_generated": check_bt_json_exists(),
        "bt_error": True,
    }
