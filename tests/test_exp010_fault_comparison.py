import pytest

from safeagent.experiments.fault_comparison import (
    compare_recovery_policies,
)
from safeagent.recovery.risk_aware import OperationRisk
from safeagent.recovery.verification import VerificationStatus


@pytest.mark.parametrize(
    "risk,status,expected_safeagent",
    [
        (OperationRisk.LOW, VerificationStatus.SUCCESS, "STOP"),
        (OperationRisk.MEDIUM, VerificationStatus.SUCCESS, "STOP"),
        (OperationRisk.HIGH, VerificationStatus.SUCCESS, "STOP"),
        (OperationRisk.LOW, VerificationStatus.NOT_EXECUTED, "RETRY"),
        (OperationRisk.MEDIUM, VerificationStatus.NOT_EXECUTED, "RETRY"),
        (OperationRisk.HIGH, VerificationStatus.NOT_EXECUTED, "ESCALATE"),
        (OperationRisk.LOW, VerificationStatus.UNKNOWN, "ESCALATE"),
        (OperationRisk.MEDIUM, VerificationStatus.UNKNOWN, "ESCALATE"),
        (OperationRisk.HIGH, VerificationStatus.UNKNOWN, "ESCALATE"),
    ],
)
def test_identical_fault_scenarios(
    risk,
    status,
    expected_safeagent,
):
    result = compare_recovery_policies(risk, status)

    assert result["naive"] == "RETRY"
    assert result["idempotent"] == "RETRY"
    assert result["checkpoint"] == "RETRY"
    assert result["safeagent"] == expected_safeagent