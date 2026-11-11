import pytest

from safeagent.agents.nodes import apply_recovery_policy


@pytest.mark.parametrize(
    "risk, status, expected",
    [
        ("LOW", "SUCCESS", "STOP"),
        ("MEDIUM", "SUCCESS", "STOP"),
        ("HIGH", "SUCCESS", "STOP"),

        ("LOW", "NOT_EXECUTED", "RETRY"),
        ("MEDIUM", "NOT_EXECUTED", "RETRY"),
        ("HIGH", "NOT_EXECUTED", "ESCALATE"),

        ("LOW", "UNKNOWN", "ESCALATE"),
        ("MEDIUM", "UNKNOWN", "ESCALATE"),
        ("HIGH", "UNKNOWN", "ESCALATE"),
    ],
)
def test_recovery_policy_node(risk, status, expected):

    state = {
        "risk": risk,
        "verification_status": status,
    }

    result = apply_recovery_policy(state)

    assert result["recovery_decision"] == expected
    assert result["recovery_reason"]