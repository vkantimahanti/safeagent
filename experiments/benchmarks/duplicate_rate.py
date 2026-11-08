import csv
import time
from pathlib import Path

from safeagent.services.utility_service import UtilityService
from safeagent.services.idempotent_utility_service import (
    IdempotentUtilityService,
)


TRIALS = 100
OUTPUT_DIR = Path("results/exp006a")


def run_naive_trial(trial_id):
    service = UtilityService()

    start = time.perf_counter()

    service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
    )

    # Simulate a retry after acknowledgment loss.
    service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "trial_id": trial_id,
        "strategy": "naive",
        "ticket_count": len(service.list_tickets()),
        "duplicate": int(len(service.list_tickets()) > 1),
        "elapsed_ms": elapsed_ms,
    }


def run_safeagent_trial(trial_id):
    service = IdempotentUtilityService()

    start = time.perf_counter()

    service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id=f"OP-{trial_id}",
    )

    # Retry the same logical operation.
    service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id=f"OP-{trial_id}",
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "trial_id": trial_id,
        "strategy": "safeagent",
        "ticket_count": len(service.list_tickets()),
        "duplicate": int(len(service.list_tickets()) > 1),
        "elapsed_ms": elapsed_ms,
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for trial_id in range(1, TRIALS + 1):
        results.append(run_naive_trial(trial_id))
        results.append(run_safeagent_trial(trial_id))

    output_file = OUTPUT_DIR / "duplicate_rate.csv"

    with output_file.open("w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "trial_id",
                "strategy",
                "ticket_count",
                "duplicate",
                "elapsed_ms",
            ],
        )

        writer.writeheader()
        writer.writerows(results)

    for strategy in ("naive", "safeagent"):
        subset = [
            result
            for result in results
            if result["strategy"] == strategy
        ]

        duplicate_rate = (
            sum(result["duplicate"] for result in subset)
            / len(subset)
        ) * 100

        average_latency = (
            sum(result["elapsed_ms"] for result in subset)
            / len(subset)
        )

        print(f"\nStrategy: {strategy}")
        print(f"Trials: {len(subset)}")
        print(f"Duplicate rate: {duplicate_rate:.2f}%")
        print(f"Average execution time: {average_latency:.4f} ms")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()