import csv
import statistics
from pathlib import Path

from safeagent.experiments.latency_benchmark import (
    measure_recovery_latency,
)


def main():
    trials = 100
    warmups = 5

    output_dir = Path("results/exp010_latency")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Warm-up runs
    for i in range(warmups):
        measure_recovery_latency(
            str(output_dir / f"warmup_{i}")
        )

    rows = []

    for i in range(trials):
        result = measure_recovery_latency(
            str(output_dir / f"trial_{i}")
        )

        rows.append({
            "trial": i,
            "idempotent_ms": result["idempotent_ms"],
            "safeagent_ms": result["safeagent_ms"],
        })

    csv_path = Path("results/exp010_latency.csv")

    with csv_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "trial",
                "idempotent_ms",
                "safeagent_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\nEXP-010: Recovery Latency Benchmark")
    print("=" * 55)

    for approach in ["idempotent", "safeagent"]:
        values = [
            row[f"{approach}_ms"]
            for row in rows
        ]

        print(f"\n{approach.upper()}")
        print(f"Mean:   {statistics.mean(values):.3f} ms")
        print(f"Median: {statistics.median(values):.3f} ms")
        print(f"Min:    {min(values):.3f} ms")
        print(f"Max:    {max(values):.3f} ms")

    print(f"\nResults saved to {csv_path}")


if __name__ == "__main__":
    main()