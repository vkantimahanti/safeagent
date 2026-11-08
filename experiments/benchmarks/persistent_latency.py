import csv
import statistics
import tempfile
import time
from pathlib import Path

from safeagent.services.utility_service import UtilityService
from safeagent.services.idempotent_utility_service import (
    IdempotentUtilityService,
)
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


TRIALS = 100
OUTPUT_DIR = Path("results/exp006b")


def benchmark_naive():
    service = UtilityService()

    start = time.perf_counter_ns()

    service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
    )

    elapsed_ns = time.perf_counter_ns() - start

    return elapsed_ns / 1_000_000


def benchmark_in_memory(trial_id):
    service = IdempotentUtilityService()

    start = time.perf_counter_ns()

    service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id=f"OP-{trial_id}",
    )

    elapsed_ns = time.perf_counter_ns() - start

    return elapsed_ns / 1_000_000


def benchmark_persistent(trial_id, db_path):
    service = PersistentUtilityService(db_path)

    start = time.perf_counter_ns()

    service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id=f"OP-{trial_id}",
    )

    elapsed_ns = time.perf_counter_ns() - start

    return elapsed_ns / 1_000_000


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "benchmark.db"

        for trial_id in range(1, TRIALS + 1):

            for strategy, benchmark in [
                ("naive", lambda: benchmark_naive()),
                (
                    "in_memory",
                    lambda: benchmark_in_memory(trial_id),
                ),
                (
                    "persistent",
                    lambda: benchmark_persistent(
                        trial_id,
                        db_path,
                    ),
                ),
            ]:

                elapsed_ms = benchmark()

                results.append({
                    "trial_id": trial_id,
                    "strategy": strategy,
                    "elapsed_ms": elapsed_ms,
                })

    output_file = OUTPUT_DIR / "persistent_latency.csv"

    with output_file.open("w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "trial_id",
                "strategy",
                "elapsed_ms",
            ],
        )

        writer.writeheader()
        writer.writerows(results)

    for strategy in ("naive", "in_memory", "persistent"):

        latencies = [
            result["elapsed_ms"]
            for result in results
            if result["strategy"] == strategy
        ]

        print(f"\nStrategy: {strategy}")
        print(f"Trials: {len(latencies)}")
        print(f"Mean latency: {statistics.mean(latencies):.4f} ms")
        print(f"Median latency: {statistics.median(latencies):.4f} ms")
        print(f"Maximum latency: {max(latencies):.4f} ms")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()