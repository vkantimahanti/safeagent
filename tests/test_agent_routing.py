import pytest

from safeagent.agents.workflow import build_workflow


@pytest.mark.parametrize(
    "operation_type, granted, expected",
    [
        ("CREATE_TICKET", False, "SIMULATED_EXECUTION"),
        ("DISCONNECT_POWER", False, "BLOCKED"),
        ("DISCONNECT_POWER", True, "SIMULATED_EXECUTION"),
    ],
)
def test_authorization_routing(operation_type, granted, expected):
    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": operation_type,
        "authorization_granted": granted,
    })

    assert result["workflow_status"] == expected

    if expected == "BLOCKED":
        assert result["authorized"] is False
        assert result.get("tool_executed") is not True
        assert result.get("verification_status") is None
        assert result.get("recovery_decision") is None

    else:
        assert result["authorized"] is True
        assert result["tool_executed"] is True
        assert result["verification_status"] == "UNKNOWN"
        assert result["recovery_decision"] == "ESCALATE"


def test_unauthorized_operation_is_blocked():
    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": "DISCONNECT_POWER",
        "authorization_granted": False,
    })

    assert result["authorized"] is False
    assert result["workflow_status"] == "BLOCKED"
    assert result.get("tool_executed") is not True
    assert result.get("recovery_decision") is None