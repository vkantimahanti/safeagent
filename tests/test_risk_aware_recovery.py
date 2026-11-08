import pytest

from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)

from safeagent.recovery.verification import (
    VerificationStatus,
    RecoveryDecision,
)


@pytest.mark.parametrize(
    "risk, verification, expected",
    [
        (
            OperationRisk.LOW,
            VerificationStatus.SUCCESS,
            RecoveryDecision.STOP,
        ),
        (
            OperationRisk.MEDIUM,
            VerificationStatus.SUCCESS,
            RecoveryDecision.STOP,
        ),
        (
            OperationRisk.HIGH,
            VerificationStatus.SUCCESS,
            RecoveryDecision.STOP,
        ),
        (
            OperationRisk.LOW,
            VerificationStatus.NOT_EXECUTED,
            RecoveryDecision.RETRY,
        ),
        (
            OperationRisk.MEDIUM,
            VerificationStatus.NOT_EXECUTED,
            RecoveryDecision.RETRY,
        ),
        (
            OperationRisk.HIGH,
            VerificationStatus.NOT_EXECUTED,
            RecoveryDecision.ESCALATE,
        ),
        (
            OperationRisk.LOW,
            VerificationStatus.UNKNOWN,
            RecoveryDecision.ESCALATE,
        ),
        (
            OperationRisk.MEDIUM,
            VerificationStatus.UNKNOWN,
            RecoveryDecision.ESCALATE,
        ),
        (
            OperationRisk.HIGH,
            VerificationStatus.UNKNOWN,
            RecoveryDecision.ESCALATE,
        ),
    ],
)
def test_risk_aware_recovery(
    risk,
    verification,
    expected,
):
    controller = RiskAwareRecoveryController()

    result = controller.decide(
        risk=risk,
        verification_status=verification,
    )

    assert result.decision == expected
    assert result.risk == risk
    assert result.verification_status == verification