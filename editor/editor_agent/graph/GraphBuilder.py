"""
Graph construction and compilation logic.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver
from editor_agent.graph.State import AgentGraphState
from editor_agent.graph.GraphNodes import (
    agent_node,
    check_csharp_errors_node,
    check_bt_errors_node,
)
from editor_agent.graph.GraphRouter import (
    route_after_csharp_check,
    route_after_bt_check,
)
from editor_agent.Config import CONFIG


def build_agent_graph() -> CompiledStateGraph:
    """Build and compile the LangGraph StateGraph for the agent.
    
    Graph structure (NEWNODE=true):
        START -> agent -> check_csharp -> (conditional) -> check_bt -> (conditional) -> END
        
    Graph structure (NEWNODE=false):
        START -> agent -> check_bt -> (conditional) -> END
        
    Nodes:
        - agent: Main ReAct agent that executes tools
        - check_csharp: Validates C# compilation status (only if NEWNODE=true)
        - check_bt: Validates BehaviorTree JSON generation and deserialization
        
    Conditional edges:
        - After check_csharp: Routes to agent (if errors), check_bt, or end
        - After check_bt: Routes to agent (if errors) or end
        
    Returns:
        CompiledStateGraph: The compiled graph ready for execution.
    """
    # Create the state graph
    workflow = StateGraph(AgentGraphState)
    
    # Define nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("check_bt", check_bt_errors_node)
    
    # Define edges
    workflow.add_edge(START, "agent")
    
    # Add C# check node and edges only if NEWNODE is enabled
    if CONFIG.NEWNODE:
        workflow.add_node("check_csharp", check_csharp_errors_node)
        workflow.add_edge("agent", "check_csharp")
        
        # Conditional edge after C# check
        workflow.add_conditional_edges(
            "check_csharp",
            route_after_csharp_check,
            {
                "check_bt": "check_bt",
                "agent": "agent",
                "end": END,
            }
        )
    else:
        # Skip C# check, go directly to BT check
        workflow.add_edge("agent", "check_bt")
    
    # Conditional edge after BT check
    workflow.add_conditional_edges(
        "check_bt",
        route_after_bt_check,
        {
            "agent": "agent",
            "end": END,
        }
    )
    
    # Compile the graph with memory checkpointing
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)
    
    return graph
