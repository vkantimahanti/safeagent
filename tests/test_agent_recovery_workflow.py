from unittest import result

import pytest

from safeagent.agents.workflow import build_workflow


@pytest.mark.parametrize(
    "operation_type, verification_status, expected",
    [
        ("READ_CUSTOMER", "SUCCESS", "STOP"),
        ("CREATE_TICKET", "SUCCESS", "STOP"),
        ("DISCONNECT_POWER", "SUCCESS", "STOP"),

        ("READ_CUSTOMER", "NOT_EXECUTED", "RETRY"),
        ("CREATE_TICKET", "NOT_EXECUTED", "RETRY"),
        ("DISCONNECT_POWER", "NOT_EXECUTED", "ESCALATE"),

        ("READ_CUSTOMER", "UNKNOWN", "ESCALATE"),
        ("CREATE_TICKET", "UNKNOWN", "ESCALATE"),
        ("DISCONNECT_POWER", "UNKNOWN", "ESCALATE"),
    ],
)
def test_end_to_end_recovery(
    operation_type,
    verification_status,
    expected,
):
    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": operation_type,
        "authorization_granted": True,
        "simulated_verification_status": verification_status,
    })

    assert result["workflow_status"] == "SIMULATED_EXECUTION"
    assert result["tool_executed"] is True
    assert result["verification_status"] == verification_status
    assert result["recovery_decision"] == expected
    assert result["recovery_reason"]

def test_unauthorized_operation_skips_recovery():
    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": "DISCONNECT_POWER",
        "authorization_granted": False,
        "simulated_verification_status": "SUCCESS",
    })

    assert result["workflow_status"] == "BLOCKED"
    assert result.get("recovery_decision") is None
    assert result.get("verification_status") is None
    assert result.get("recovery_reason") is None