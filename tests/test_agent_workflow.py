import pytest

from safeagent.agents.workflow import build_workflow

@pytest.mark.parametrize(
    "operation_type, expected_risk, expected_auth",
    [
        ("READ_CUSTOMER", "LOW", False),
        ("CREATE_TICKET", "MEDIUM", False),
        ("DISCONNECT_POWER", "HIGH", True),
    ],
)
def test_workflow_loads_trusted_policy(
    operation_type,
    expected_risk,
    expected_auth,
):
    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": operation_type,
        "operation_id": "OP-1001",
        "customer_id": "CUST-101",
        "issue": "Power outage",
    })

    assert result["risk"] == expected_risk
    assert result["requires_authorization"] == expected_auth

def test_workflow_rejects_unknown_operation():
    workflow = build_workflow()

    with pytest.raises(ValueError):
        workflow.invoke({
            "operation_type": "UNKNOWN_OPERATION",
        })