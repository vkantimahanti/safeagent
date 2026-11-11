import pytest

from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus


@pytest.mark.parametrize(
    "risk,status,expected",
    [
        (OperationRisk.LOW, VerificationStatus.UNKNOWN, "ESCALATE"),
        (OperationRisk.MEDIUM, VerificationStatus.UNKNOWN, "ESCALATE"),
        (OperationRisk.HIGH, VerificationStatus.UNKNOWN, "ESCALATE"),

        (OperationRisk.LOW, VerificationStatus.NOT_EXECUTED, "RETRY"),
        (OperationRisk.MEDIUM, VerificationStatus.NOT_EXECUTED, "RETRY"),
        (OperationRisk.HIGH, VerificationStatus.NOT_EXECUTED, "ESCALATE"),

        (OperationRisk.LOW, VerificationStatus.SUCCESS, "STOP"),
        (OperationRisk.MEDIUM, VerificationStatus.SUCCESS, "STOP"),
        (OperationRisk.HIGH, VerificationStatus.SUCCESS, "STOP"),
    ],
)
def test_exp010_risk_decisions(risk, status, expected):
    controller = RiskAwareRecoveryController()

    result = controller.decide(
        risk=risk,
        verification_status=status,
    )

    assert result.decision.value == expected