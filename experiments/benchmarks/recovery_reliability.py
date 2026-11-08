import asyncio
import csv
import tempfile
import time
from pathlib import Path

import httpx

from safeagent.api.dependencies import get_service
from safeagent.api.main import app

from safeagent.faults.http_acknowledgment_loss import (
    HTTPAcknowledgmentLossTransport,
    HTTPVerificationFailureTransport,
)

from safeagent.recovery.async_http_client import (
    AsyncSafeAgentHTTPRecoveryClient,
)

from safeagent.recovery.verification import RecoveryDecision

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


TRIALS = 100
OUTPUT_DIR = Path("results/exp006g")


async def run_trial(scenario, trial_id, db_path):
    service = PersistentUtilityService(db_path)

    app.dependency_overrides[get_service] = lambda: service

    operation_id = f"OP-{scenario}-{trial_id}"

    try:
        underlying = httpx.ASGITransport(app=app)

        if scenario == "A":
            transport = HTTPAcknowledgmentLossTransport(
                underlying
            )

        elif scenario == "B":
            transport = HTTPAcknowledgmentLossTransport(
                HTTPVerificationFailureTransport(
                    underlying
                )
            )

        else:
            transport = underlying

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:

            recovery_client = AsyncSafeAgentHTTPRecoveryClient(
                client
            )

            payload = {
                "customer_id": "CUST-101",
                "issue": "Power outage",
                "operation_id": operation_id,
            }

            if scenario in ("A", "B"):
                try:
                    await client.post("/tickets", json=payload)
                except httpx.ReadTimeout:
                    pass

            start = time.perf_counter()

            decision = await recovery_client.recover(
                operation_id
            )

            recovery_ms = (
                time.perf_counter() - start
            ) * 1000

            expected = (
                RecoveryDecision.STOP
                if scenario == "A"
                else RecoveryDecision.ESCALATE
            )

            return {
                "scenario": scenario,
                "trial_id": trial_id,
                "decision": decision.value,
                "expected_decision": expected.value,
                "correct": int(decision == expected),
                "recovery_ms": recovery_ms,
            }

    finally:
        app.dependency_overrides.clear()


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "recovery.db"

        for scenario in ("A", "B", "C"):
            for trial_id in range(1, TRIALS + 1):
                result = await run_trial(
                    scenario,
                    trial_id,
                    db_path,
                )
                rows.append(result)

    output_file = OUTPUT_DIR / "recovery_reliability.csv"

    with output_file.open("w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "scenario",
                "trial_id",
                "decision",
                "expected_decision",
                "correct",
                "recovery_ms",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\nEXP-006G RESULTS")

    for scenario in ("A", "B", "C"):
        subset = [
            row for row in rows
            if row["scenario"] == scenario
        ]

        correct = sum(row["correct"] for row in subset)

        accuracy = correct / len(subset) * 100

        mean_recovery_ms = (
            sum(row["recovery_ms"] for row in subset)
            / len(subset)
        )

        print(f"\nScenario: {scenario}")
        print(f"Trials: {len(subset)}")
        print(f"Decision accuracy: {accuracy:.2f}%")
        print(
            f"Mean recovery latency: "
            f"{mean_recovery_ms:.4f} ms"
        )

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())