import random
from collections import Counter

from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus


def run_randomized_healthcare_experiment(
    trials: int = 1000,
    seed: int = 42,
):
    rng = random.Random(seed)
    controller = RiskAwareRecoveryController()

    statuses = [
        VerificationStatus.SUCCESS,
        VerificationStatus.NOT_EXECUTED,
        VerificationStatus.UNKNOWN,
    ]

    results = []

    for trial in range(trials):
        status = rng.choice(statuses)

        safeagent_decision = controller.decide(
            risk=OperationRisk.MEDIUM,
            verification_status=status,
        ).decision.value

        results.append({
            "trial": trial + 1,
            "verification_status": status.value,
            "baseline_decision": "RETRY",
            "safeagent_decision": safeagent_decision,
        })

    return results


def summarize_randomized_experiment(results):
    summary = {
        "total_trials": len(results),
        "verification_statuses": dict(
            Counter(row["verification_status"] for row in results)
        ),
        "baseline_decisions": dict(
            Counter(row["baseline_decision"] for row in results)
        ),
        "safeagent_decisions": dict(
            Counter(row["safeagent_decision"] for row in results)
        ),
    }

    return summary