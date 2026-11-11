import csv
import random
from pathlib import Path

from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus


def run_benchmark(
    trials: int = 1000,
    seed: int = 42,
    output_path: str = "results/exp010_results.csv",
):
    rng = random.Random(seed)
    controller = RiskAwareRecoveryController()

    risks = list(OperationRisk)
    statuses = list(VerificationStatus)

    rows = []

    for trial in range(trials):
        risk = rng.choice(risks)
        status = rng.choice(statuses)

        safeagent = controller.decide(
            risk=risk,
            verification_status=status,
        ).decision.value

        decisions = {
            "naive": "RETRY",
            "idempotent": "RETRY",
            "checkpoint_stable": "RETRY",
            "safeagent": safeagent,
        }

        for approach, decision in decisions.items():
            rows.append({
                "trial": trial,
                "risk": risk.value,
                "verification_status": status.value,
                "approach": approach,
                "decision": decision,
                "retry_attempted": int(decision == "RETRY"),
                "escalated": int(decision == "ESCALATE"),
            })

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "trial",
                "risk",
                "verification_status",
                "approach",
                "decision",
                "retry_attempted",
                "escalated",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return rows


def summarize_benchmark(rows: list[dict]) -> dict:
    summary = {}

    approaches = sorted(set(row["approach"] for row in rows))

    for approach in approaches:
        records = [
            row for row in rows
            if row["approach"] == approach
        ]

        total = len(records)

        retries = sum(row["retry_attempted"] for row in records)
        escalations = sum(row["escalated"] for row in records)
        stops = sum(row["decision"] == "STOP" for row in records)

        unnecessary_retries = sum(
            row["decision"] == "RETRY"
            and row["verification_status"] == "SUCCESS"
            for row in records
        )

        unsafe_retry_decisions = sum(
            row["decision"] == "RETRY"
            and (
                row["verification_status"] == "UNKNOWN"
                or (
                    row["risk"] == "HIGH"
                    and row["verification_status"] == "NOT_EXECUTED"
                )
            )
            for row in records
        )

        summary[approach] = {
            "total": total,
            "retries": retries,
            "escalations": escalations,
            "stops": stops,
            "unnecessary_retries": unnecessary_retries,
            "policy_unsafe_retries": unsafe_retry_decisions,
            "retry_rate": round(retries / total, 4),
            "escalation_rate": round(escalations / total, 4),
        }

    return summary