import pytest

from safeagent.agents.nodes import verify_simulated_outcome


@pytest.mark.parametrize(
    "verification_status, expected",
    [
        ("SUCCESS", "SUCCESS"),
        ("NOT_EXECUTED", "NOT_EXECUTED"),
        ("UNKNOWN", "UNKNOWN"),
        ("INVALID", "UNKNOWN"),
    ],
)
def test_simulated_verification(
    verification_status,
    expected,
):
    result = verify_simulated_outcome({
        "tool_executed": True,
        "simulated_verification_status": verification_status,
    })

    assert result["verification_status"] == expected


def test_verification_without_execution():
    result = verify_simulated_outcome({
        "tool_executed": False,
        "simulated_verification_status": "SUCCESS",
    })

    assert result["verification_status"] == "UNKNOWN"