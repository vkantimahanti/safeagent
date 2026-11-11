import pytest

from safeagent.agents.workflow import build_workflow

@pytest.mark.parametrize(
    "operation_type, granted, expected",
    [
        ("CREATE_TICKET", False, True),
        ("DISCONNECT_POWER", False, False),
        ("DISCONNECT_POWER", True, True),
    ],
)
def test_authorization(operation_type, granted, expected):
    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": operation_type,
        "authorization_granted": granted,
    })

    assert result["authorized"] is expected