from unittest import result

import pytest

from safeagent.agents.workflow import build_workflow


@pytest.mark.parametrize(
    "operation_type, granted, expected_execution",
    [
        ("CREATE_TICKET", False, True),
        ("DISCONNECT_POWER", False, False),
        ("DISCONNECT_POWER", True, True),
    ],
)
def test_simulated_execution(
    operation_type,
    granted,
    expected_execution,
):
    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": operation_type,
        "authorization_granted": granted,
    })

    assert result.get("tool_executed", False) is expected_execution



def test_unauthorized_operation_never_reaches_execution(monkeypatch):
    from safeagent.agents import workflow as workflow_module

    calls = []

    def tracked_execution(state):
        calls.append(state["operation_type"])
        return {"tool_executed": True}

    monkeypatch.setattr(
        workflow_module,
        "execute_simulated_tool",
        tracked_execution,
    )

    workflow = workflow_module.build_workflow()

    result = workflow.invoke({
        "operation_type": "DISCONNECT_POWER",
        "authorization_granted": False,
    })

    assert calls == []
    assert result["workflow_status"] == "BLOCKED"
    assert result.get("recovery_decision") is None