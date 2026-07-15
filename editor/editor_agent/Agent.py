"""
Main agent execution module.

This module provides the entry point for running the LangGraph-based agent.
The agent graph is constructed from modular components defined in the graph package.
"""

import os
import pathlib
import uuid
from dotenv import load_dotenv
from editor_agent.graph import build_agent_graph
from editor_agent.graph.State import create_initial_state
from editor_agent.Config import CONFIG
from editor_agent.Logging import LOGGER

dotenv_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path)

RECURSION_LIMIT = 500

def run_agent(user_input: str) -> dict:
    """Run the agent with the given user input.
    
    This function:
    1. Builds the agent graph
    2. Creates the initial state with the user's input
    3. Executes the graph
    4. Returns the final state
    
    Args:
        user_input: The user's request or query.
        
    Returns:
        dict: Final state containing messages and compilation status.
    """
    # Build the graph
    graph = build_agent_graph()
    
    # Create initial state
    initial_state = create_initial_state(user_input)
    
    # Log initialization
    LOGGER.log(f"Starting agent with user input: {user_input}")
    LOGGER.log(f"Initial state - bt_generated: {initial_state['bt_generated']}")
    
    # Generate a unique thread_id for this execution
    thread_id = str(uuid.uuid4())
    
    # Run the graph with checkpointer configuration
    final_state = graph.invoke(
        initial_state,
        config={
            "recursion_limit": RECURSION_LIMIT,
            "configurable": {"thread_id": thread_id}
        }
    )
    
    return final_state


if __name__ == "__main__":
    # Initialize configuration
    project_dir = os.getenv("PROJECT_DIRECTORY")
    CONFIG.PROJECT_DIRECTORY = pathlib.Path(project_dir)

    # Run agent with sample input
    user_input = "Create behavior tree that can validly play the dodgeball game well"
    output = run_agent(user_input=user_input)
    
    print(output)
