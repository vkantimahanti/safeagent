from langgraph.graph import StateGraph, START, END
from safeagent.agents.state import SafeAgentState
from safeagent.agents.nodes import (
    apply_recovery_policy,
    load_operation_policy,
    check_authorization,
    route_authorization,
    blocked_node,
    execute_simulated_tool,
    verify_simulated_outcome,
)
from safeagent.agents.llm_proposal import simulate_llm_proposal
from langgraph.checkpoint.memory import MemorySaver

def build_workflow(checkpointer=None):
    graph = StateGraph(SafeAgentState)

    graph.add_node("load_policy", load_operation_policy)
    graph.add_node("authorization_check", check_authorization)
    graph.add_node("execute_tool", execute_simulated_tool)
    graph.add_node("verify_outcome", verify_simulated_outcome)
    graph.add_node("recovery_policy", apply_recovery_policy)
    graph.add_node("blocked", blocked_node)

    graph.add_edge(START, "load_policy")
    graph.add_edge("load_policy", "authorization_check")

    graph.add_conditional_edges(
        "authorization_check",
        route_authorization,
        {
            "approved": "execute_tool",
            "blocked": "blocked",
        },
    )

    graph.add_edge("execute_tool", "verify_outcome")
    graph.add_edge("verify_outcome", "recovery_policy")
    graph.add_edge("recovery_policy", END)
    graph.add_edge("blocked", END)

    return graph.compile(checkpointer=checkpointer)


proposal = simulate_llm_proposal(
    "Please create ticket for this customer"
)

workflow = build_workflow()


result = workflow.invoke({
    "operation_type": proposal.operation_type,
    "authorization_granted": False,
})

print("Operation:", result["operation_type"])
print("Risk:", result["risk"])
print("Authorized:", result["authorized"])
print("Workflow Status:", result["workflow_status"])
print("Recovery Decision:", result.get("recovery_decision"))