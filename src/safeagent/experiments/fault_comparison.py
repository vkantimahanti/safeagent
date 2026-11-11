from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus


def compare_recovery_policies(
    risk: OperationRisk,
    status: VerificationStatus,
) -> dict:
    """
    Compare recovery decisions under the same failure scenario.

    These are explicitly defined benchmark policies,
    not universal behaviors of these technologies.
    """

    # Baseline A: Always retry after an uncertain response.
    naive_decision = "RETRY"

    # Baseline B: Retry using a stable operation ID.
    # Idempotency protects against duplicate side effects
    # only when the downstream service enforces it.
    idempotent_decision = "RETRY"

    # Baseline C: Checkpoint indicates tool completion
    # was not recorded; retry using the same operation ID.
    checkpoint_decision = "RETRY"

    # Approach D: SafeAgent verifies outcome and considers risk.
    controller = RiskAwareRecoveryController()

    safeagent_result = controller.decide(
        risk=risk,
        verification_status=status,
    )

    return {
        "risk": risk.value,
        "verification_status": status.value,
        "naive": naive_decision,
        "idempotent": idempotent_decision,
        "checkpoint": checkpoint_decision,
        "safeagent": safeagent_result.decision.value,
    }