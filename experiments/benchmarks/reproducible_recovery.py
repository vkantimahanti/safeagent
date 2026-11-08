import asyncio
import csv
import platform
import random
import sqlite3
import statistics
import tempfile
import time

from pathlib import Path

import httpx

from safeagent.api.dependencies import get_service
from safeagent.api.main import app

from safeagent.faults.http_acknowledgment_loss import (
    HTTPAcknowledgmentLossTransport,
    DelayedVerificationFailureTransport,
)

from safeagent.recovery.async_http_client import (
    AsyncSafeAgentHTTPRecoveryClient,
)

from safeagent.recovery.verification import RecoveryDecision

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


TRIALS_PER_SCENARIO = 100
RANDOM_SEED = 42
VERIFICATION_DELAY_SECONDS = 0.05

OUTPUT_DIR = Path("results/exp006h")


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
                DelayedVerificationFailureTransport(
                    underlying,
                    delay_seconds=VERIFICATION_DELAY_SECONDS,
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

            start = time.perf_counter()

            post_timeout_observed = False

            if scenario in ("A", "B"):
                try:
                    await client.post("/tickets", json=payload)
                except httpx.ReadTimeout:
                    post_timeout_observed = True

                assert post_timeout_observed, (
                    "Expected simulated POST acknowledgment loss"
                )

            decision = await recovery_client.recover(
                operation_id
            )

            elapsed_ms = (
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
                "end_to_end_ms": elapsed_ms,
            }

    finally:
        app.dependency_overrides.clear()


async def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = [
        (scenario, trial_id)
        for scenario in ("A", "B", "C")
        for trial_id in range(1, TRIALS_PER_SCENARIO + 1)
    ]

    random.Random(RANDOM_SEED).shuffle(scenarios)

    rows = []

    with tempfile.TemporaryDirectory() as temp_dir:

        db_path = Path(temp_dir) / "reproducible.db"

        for scenario, trial_id in scenarios:

            result = await run_trial(
                scenario,
                trial_id,
                db_path,
            )

            rows.append(result)

    output_file = OUTPUT_DIR / "reproducible_recovery.csv"

    with output_file.open("w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "scenario",
                "trial_id",
                "decision",
                "expected_decision",
                "correct",
                "end_to_end_ms",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\nEXP-006H RESULTS")

    for scenario in ("A", "B", "C"):

        subset = [
            row for row in rows
            if row["scenario"] == scenario
        ]

        latencies = [
            row["end_to_end_ms"]
            for row in subset
        ]

        correct = sum(row["correct"] for row in subset)

        print(f"\nScenario: {scenario}")
        print(f"Trials: {len(subset)}")
        print(
            f"Decision accuracy: "
            f"{correct / len(subset) * 100:.2f}%"
        )
        print(
            f"Mean latency: "
            f"{statistics.mean(latencies):.4f} ms"
        )
        print(
            f"Median latency: "
            f"{statistics.median(latencies):.4f} ms"
        )

    print("\nENVIRONMENT")
    print(f"Python: {platform.python_version()}")
    print(f"OS: {platform.platform()}")
    print(f"SQLite: {sqlite3.sqlite_version}")
    print(f"Random seed: {RANDOM_SEED}")
    print(
        f"Verification delay: "
        f"{VERIFICATION_DELAY_SECONDS * 1000:.0f} ms"
    )

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())