import csv
import statistics
import tempfile
import time

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


WORKER_COUNTS = [1, 2, 5, 10]
REPEATS = 10

OUTPUT_DIR = Path("results/exp006c")


def execute_operation(db_path, operation_id):
    service = PersistentUtilityService(db_path)

    start = time.perf_counter()

    ticket = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id=operation_id,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    return ticket.ticket_id, elapsed_ms


def run_trial(db_path, worker_count, trial_id):

    operation_id = f"OP-{worker_count}-{trial_id}"

    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=worker_count) as executor:

        futures = [
            executor.submit(
                execute_operation,
                db_path,
                operation_id,
            )
            for _ in range(worker_count)
        ]

        results = [future.result() for future in futures]

    wall_time_ms = (time.perf_counter() - start) * 1000

    ticket_ids = [result[0] for result in results]
    latencies = [result[1] for result in results]

    assert len(set(ticket_ids)) == 1, (
        "Workers returned different ticket IDs"
    )

    return {
        "worker_count": worker_count,
        "trial_id": trial_id,
        "wall_time_ms": wall_time_ms,
        "mean_worker_latency_ms": statistics.mean(latencies),
        "max_worker_latency_ms": max(latencies),
        "unique_ticket_ids": len(set(ticket_ids)),
    }


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []

    with tempfile.TemporaryDirectory() as temp_dir:

        db_path = Path(temp_dir) / "concurrent.db"

        for worker_count in WORKER_COUNTS:

            for trial_id in range(1, REPEATS + 1):

                result = run_trial(
                    db_path,
                    worker_count,
                    trial_id,
                )

                rows.append(result)

                print(
                    f"Workers={worker_count}, "
                    f"Trial={trial_id}, "
                    f"Wall time={result['wall_time_ms']:.2f} ms"
                )

    output_file = OUTPUT_DIR / "concurrent_workload.csv"

    with output_file.open("w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "worker_count",
                "trial_id",
                "wall_time_ms",
                "mean_worker_latency_ms",
                "max_worker_latency_ms",
                "unique_ticket_ids",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\nSUMMARY")

    for worker_count in WORKER_COUNTS:

        subset = [
            row
            for row in rows
            if row["worker_count"] == worker_count
        ]

        mean_wall_time = statistics.mean(
            row["wall_time_ms"] for row in subset
        )

        print(
            f"Workers={worker_count}: "
            f"Mean wall time={mean_wall_time:.2f} ms"
        )

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()