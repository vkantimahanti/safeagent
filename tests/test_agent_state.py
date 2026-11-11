from safeagent.agents.state import SafeAgentState

def test_agent_state_initialization():
    state: SafeAgentState = {
        "operation_type": "CREATE_TICKET",
        "operation_id": "OP-1001",
        "customer_id": "CUST-101",
        "issue": "Power outage",
    }

    assert state["operation_type"] == "CREATE_TICKET"
    assert state["operation_id"] == "OP-1001"
    assert state["customer_id"] == "CUST-101"