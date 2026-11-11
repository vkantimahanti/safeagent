from langgraph.graph import StateGraph, START, END

from safeagent.agents.state import SafeAgentState
from safeagent.agents.nodes import (
    load_operation_policy,
    verify_persistent_outcome,
    apply_recovery_policy,
)


def build_persistent_recovery_workflow(checkpointer=None):
    graph = StateGraph(SafeAgentState)

    graph.add_node("load_policy", load_operation_policy)
    graph.add_node("verify_outcome", verify_persistent_outcome)
    graph.add_node("recovery_policy", apply_recovery_policy)

    graph.add_edge(START, "load_policy")
    graph.add_edge("load_policy", "verify_outcome")
    graph.add_edge("verify_outcome", "recovery_policy")
    graph.add_edge("recovery_policy", END)

    return graph.compile(checkpointer=checkpointer)