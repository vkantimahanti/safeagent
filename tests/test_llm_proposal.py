import pytest

from safeagent.agents.llm_proposal import simulate_llm_proposal
from safeagent.agents.workflow import build_workflow


@pytest.mark.parametrize(
    "user_prompt, expected_operation",
    [
        ("Please create ticket", "CREATE_TICKET"),
        ("Please read customer", "READ_CUSTOMER"),
        ("Please disconnect power", "DISCONNECT_POWER"),
    ],
)
def test_llm_proposal(user_prompt, expected_operation):
    proposal = simulate_llm_proposal(user_prompt)

    assert proposal.operation_type == expected_operation


def test_high_risk_proposal_is_blocked_without_authorization():
    proposal = simulate_llm_proposal(
        "Please disconnect power"
    )

    workflow = build_workflow()

    result = workflow.invoke({
        "operation_type": proposal.operation_type,
        "authorization_granted": False,
    })

    assert result["risk"] == "HIGH"
    assert result["authorized"] is False
    assert result["workflow_status"] == "BLOCKED"
    assert result.get("tool_executed") is not True
    assert result.get("recovery_decision") is None


def test_unsupported_proposal_is_rejected():
    with pytest.raises(ValueError):
        simulate_llm_proposal(
            "Please transfer money"
        )