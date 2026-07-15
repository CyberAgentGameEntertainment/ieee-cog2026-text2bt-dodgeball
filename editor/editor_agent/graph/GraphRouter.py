"""
Routing logic (conditional edges) for the agent graph.
"""

from typing import Literal
from editor_agent.graph.State import AgentGraphState
from editor_agent.Config import CONFIG
from editor_agent.Logging import LOGGER


def route_after_csharp_check(state: AgentGraphState) -> Literal["check_bt", "agent", "end"]:
    """Determine next step after C# error check.
    
    Decision logic:
    1. If NEWNODE=true AND csharp_error=true -> return to agent for fixes
    2. If bt_generated=false -> check BT status
    3. Otherwise -> check BT
    
    Args:
        state: Current agent graph state.
        
    Returns:
        str: Name of the next node to execute ("check_bt", "agent", or "end").
    """
    # If NEWNODE is enabled and there are C# errors, go back to agent
    if CONFIG.NEWNODE and state['csharp_error']:
        LOGGER.log("C# errors exist (NEWNODE=true), returning to agent")
        return "agent"
    
    # If BT not generated yet, check BT status
    if not state['bt_generated']:
        LOGGER.log("BT not generated yet, checking BT status")
        return "check_bt"
    
    # Check BT errors
    LOGGER.log("C# errors resolved or NEWNODE=false, checking BT")
    return "check_bt"


def route_after_bt_check(state: AgentGraphState) -> Literal["agent", "end"]:
    """Determine next step after BT error check.
    
    Decision logic:
    1. If bt_generated=false -> return to agent for generation
    2. If bt_error=true -> return to agent for fixes
    3. If NEWNODE=true AND csharp_error=true -> return to agent for C# fixes
    4. Otherwise -> workflow complete (END)
    
    Args:
        state: Current agent graph state.
        
    Returns:
        str: Name of the next node to execute ("agent" or "end").
    """
    # If BT not generated, go back to agent
    if not state['bt_generated']:
        LOGGER.log("BT not generated, returning to agent")
        return "agent"
    
    # If BT has errors, go back to agent
    if state['bt_error']:
        LOGGER.log("BT deserialization errors exist, returning to agent")
        return "agent"
    
    # If NEWNODE is enabled and we need to check C# errors again
    if CONFIG.NEWNODE and state['csharp_error']:
        LOGGER.log("C# errors still exist (NEWNODE=true), returning to agent")
        return "agent"
    
    # All checks passed
    LOGGER.log("All checks passed, ending workflow")
    return "end"
