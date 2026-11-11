from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus


def test_unknown_outcome_blocks_automatic_retry():
    controller = RiskAwareRecoveryController()

    # Simulate a medium-risk healthcare administrative operation.
    risk = OperationRisk.MEDIUM

    # Verification service cannot establish the outcome.
    verification_status = VerificationStatus.UNKNOWN

    result = controller.decide(
        risk=risk,
        verification_status=verification_status,
    )

    assert result.decision.value == "ESCALATE"