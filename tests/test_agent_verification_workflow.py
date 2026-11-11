from unittest import result

import pytest

from safeagent.agents.workflow import build_workflow


@pytest.mark.parametrize(
    "status",
    ["SUCCESS", "NOT_EXECUTED", "UNKNOWN"],
)
def test_verification_workflow(status):
    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": "CREATE_TICKET",
        "authorization_granted": False,
        "simulated_verification_status": status,
    })

    assert result["tool_executed"] is True
    assert result["verification_status"] == status


def test_blocked_operation_skips_verification():
    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": "DISCONNECT_POWER",
        "authorization_granted": False,
        "simulated_verification_status": "SUCCESS",
    })

    assert result["workflow_status"] == "BLOCKED"
    assert result.get("recovery_decision") is None
    assert result.get("verification_status") is None
    assert result.get("verification_status") is None