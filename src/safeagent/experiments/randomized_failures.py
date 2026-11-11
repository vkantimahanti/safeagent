import random
from collections import Counter

from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus


def run_randomized_experiment(
    trials: int = 1000,
    seed: int = 42,
):
    rng = random.Random(seed)

    controller = RiskAwareRecoveryController()

    risks = list(OperationRisk)
    statuses = list(VerificationStatus)

    results = Counter()

    for _ in range(trials):
        risk = rng.choice(risks)
        status = rng.choice(statuses)

        decision = controller.decide(
            risk=risk,
            verification_status=status,
        )

        results[
            (risk.value, status.value, decision.decision.value)
        ] += 1

    return results