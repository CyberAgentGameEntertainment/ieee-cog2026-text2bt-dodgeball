"""
Node functions for the agent graph.
"""

import os
from dataclasses import asdict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from editor_agent.Config import CONFIG
from editor_agent.graph.State import AgentGraphState, check_bt_json_exists
from editor_agent.tools.Editing import (
    listup_folders_with_cs,
    listup_cs_files,
    read_file,
    read_behavior_tree_plan,
    write_behavior_tree_plan,
    write_behavior_tree_cs_file,
    write_behavior_tree_json,
    read_behavior_tree_json,
    grep_cs_files,
    fetch_unity_compile_results,
    fetch_bt_compile_result,
)
from editor_agent.tools.UnityCompilation import fetch_unity_compile
from editor_agent.tools.BtDeserialization import fetch_bt_deserialization_result
from editor_agent.Config import CONFIG
from editor_agent.Logging import LOGGER
from editor_agent.PromptBuilder import PROMPT_BUILDER


_MODEL_ALIASES = {
    "gpt":    "gpt-5.2-2025-12-11",
    "claude": "claude-sonnet-4-6",
    "gemini": "gemini-2.5-pro",
}


def _create_llm():
    """Create LLM instance based on CONFIG.MODEL.

    Short aliases are resolved first:
      gpt → gpt-5.2-2025-12-11
      claude → claude-sonnet-4-6  (latest Sonnet)
      gemini → gemini-2.5-pro     (latest Pro)

    Provider is then inferred from the model name prefix:
      - claude-*  → Anthropic (uses CLAUDE_API_KEY)
      - gemini-*  → Google    (uses GEMINI_API_KEY)
      - anything else → OpenAI (uses OPENAI_API_KEY)
    """
    model = _MODEL_ALIASES.get(CONFIG.MODEL, CONFIG.MODEL)

    if model.startswith("claude-"):
        from langchain_anthropic import ChatAnthropic
        api_key = os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        return ChatAnthropic(model=model, temperature=CONFIG.TEMPERATURE, api_key=api_key)

    if model.startswith("gemini-"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(model=model, temperature=CONFIG.TEMPERATURE, google_api_key=api_key)

    return ChatOpenAI(model=model, temperature=CONFIG.TEMPERATURE)


# Tool list used by the agent
AGENT_TOOLS = [
    listup_folders_with_cs,
    listup_cs_files,
    read_file,
    read_behavior_tree_plan,
    write_behavior_tree_plan,
    write_behavior_tree_cs_file,
    write_behavior_tree_json,
    read_behavior_tree_json,
    grep_cs_files,
    fetch_unity_compile_results,
    fetch_bt_compile_result,
]


def agent_node(state: AgentGraphState) -> dict:
    """Node that runs the reactive agent with tools.
    
    This node creates a ReAct agent with access to all tools and executes
    it with the current state's messages.
    
    Args:
        state: Current agent graph state.
        
    Returns:
        dict: Updated state with new messages from the agent.
    """
    LOGGER.log("=== Agent Node Start ===")
    
    # Create system message with current state context
    system_message = _build_system_message(state)
    
    # Create LLM
    llm = _create_llm()
    
    # Create react agent
    agent_executor = create_react_agent(llm, AGENT_TOOLS)
    
    # Prepare state with system message prepended
    messages_with_system = [SystemMessage(content=system_message)] + state["messages"]

    # Claude requires the last message to be a human message.
    # When the graph loops back after error checks, the tail may be an AIMessage.
    if isinstance(messages_with_system[-1], AIMessage):
        messages_with_system.append(HumanMessage(content="Please continue fixing the errors."))

    # Invoke the agent
    result = agent_executor.invoke({"messages": messages_with_system})
    
    # Remove the system message from the result to avoid duplication
    # Only return the new messages (excluding the system message we added)
    result_messages = result["messages"][1:]  # Skip the system message
    
    # Log the last message
    if result_messages:
        last_msg = result_messages[-1]
        content = getattr(last_msg, "content", str(last_msg))
        preview = content[:200] if len(content) > 200 else content
        LOGGER.log(f"Agent response: {preview}...")
    
    LOGGER.log("=== Agent Node End ===")
    
    return {"messages": result_messages}


def check_csharp_errors_node(state: AgentGraphState) -> dict:
    """Node that checks for C# compilation errors.
    
    Connects to Unity via socket to fetch compilation results.
    Only performs checks if CONFIG.NEWNODE is True.
    
    Args:
        state: Current agent graph state.
        
    Returns:
        dict: Updated state with csharp_error status.
    """
    LOGGER.log("=== Check C# Errors Node ===")
    
    if not CONFIG.NEWNODE:
        LOGGER.log("NEWNODE is False, skipping C# error check")
        return {"csharp_error": False}
    
    # Fetch compilation results
    compile_results = fetch_unity_compile()
    results_dicts = [asdict(result) for result in compile_results]
    
    has_errors = len(compile_results) > 0
    
    LOGGER.log(f"C# compilation check: {len(compile_results)} errors found")
    if has_errors:
        LOGGER.log(f"Errors: {results_dicts}")
    
    return {"csharp_error": has_errors}


def check_bt_errors_node(state: AgentGraphState) -> dict:
    """Node that checks for BehaviorTree deserialization errors.
    
    First checks if the BehaviorTree.json file exists, then attempts
    to deserialize it via Unity socket connection.
    
    Args:
        state: Current agent graph state.
        
    Returns:
        dict: Updated state with bt_generated and bt_error status.
    """
    LOGGER.log("=== Check BT Errors Node ===")
    
    # Check if BT JSON exists
    bt_exists = check_bt_json_exists()
    
    if not bt_exists:
        LOGGER.log("BehaviorTree JSON does not exist yet")
        return {"bt_generated": False, "bt_error": True}
    
    # Check BT deserialization
    bt_path = "Assets/BehaviorTree/BehaviorTree.json"
    result = fetch_bt_deserialization_result(bt_path)
    
    has_errors = "error" in result.lower() or "exception" in result.lower()
    
    LOGGER.log(f"BT deserialization check - Generated: True, Has errors: {has_errors}")
    LOGGER.log(f"Result: {result}")
    
    return {"bt_generated": True, "bt_error": has_errors}


def _build_system_message(state: AgentGraphState) -> str:
    """Build system message with current state context.
    
    Constructs a comprehensive system prompt that includes:
    - Base prompt from PromptBuilder
    - Current compilation/generation status
    - Important warnings based on current state
    
    Args:
        state: Current agent graph state.
        
    Returns:
        str: Complete system message for the agent.
    """
    base_prompt = PROMPT_BUILDER.build_system_prompt()
    
    status_info = "\n\n=== Current Status ==="
    status_info += f"\n- C# compilation errors exist: {state['csharp_error']}"
    status_info += f"\n- BehaviorTree JSON generated: {state['bt_generated']}"
    status_info += f"\n- BT deserialization errors exist: {state['bt_error']}"
    
    if CONFIG.NEWNODE and state['csharp_error']:
        status_info += "\n\n⚠️ IMPORTANT: You MUST fix all C# compilation errors before completion."
    
    if not state['bt_generated']:
        status_info += "\n\n⚠️ IMPORTANT: You MUST generate BehaviorTree JSON."
    elif state['bt_error']:
        status_info += "\n\n⚠️ IMPORTANT: You MUST fix all BehaviorTree deserialization errors before completion."
    
    return base_prompt + status_info
