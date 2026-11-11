import csv
import json
import statistics
import time
from collections import Counter
from pathlib import Path

from safeagent.healthcare.randomized_experiment import (
    run_randomized_healthcare_experiment,
    summarize_randomized_experiment,
)
from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)
from safeagent.recovery.verification import VerificationStatus


OUTPUT_DIR = Path("results/healthcare")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRIALS = 1000
SEED = 42


def measure_decision_latency(results):
    controller = RiskAwareRecoveryController()

    latencies_ms = []

    for row in results:
        status = VerificationStatus(
            row["verification_status"]
        )

        start = time.perf_counter_ns()

        controller.decide(
            risk=OperationRisk.MEDIUM,
            verification_status=status,
        )

        elapsed_ms = (
            time.perf_counter_ns() - start
        ) / 1_000_000

        latencies_ms.append(elapsed_ms)

    return {
        "mean_ms": statistics.mean(latencies_ms),
        "median_ms": statistics.median(latencies_ms),
        "p95_ms": sorted(latencies_ms)[
            int(0.95 * (len(latencies_ms) - 1))
        ],
    }


def main():
    results = run_randomized_healthcare_experiment(
        trials=TRIALS,
        seed=SEED,
    )

    summary = summarize_randomized_experiment(results)

    safeagent_counts = Counter(
        row["safeagent_decision"]
        for row in results
    )

    baseline_retries = sum(
        row["baseline_decision"] == "RETRY"
        for row in results
    )

    safeagent_retries = safeagent_counts["RETRY"]

    retry_reduction_pct = (
        (baseline_retries - safeagent_retries)
        / baseline_retries
        * 100
    )

    # Under the experimental policy assumptions:
    # Retrying SUCCESS or UNKNOWN is classified as unsafe.
    unsafe_baseline = sum(
        row["baseline_decision"] == "RETRY"
        and row["verification_status"]
        in {"SUCCESS", "UNKNOWN"}
        for row in results
    )

    unsafe_safeagent = sum(
        row["safeagent_decision"] == "RETRY"
        and row["verification_status"]
        in {"SUCCESS", "UNKNOWN"}
        for row in results
    )

    latency = measure_decision_latency(results)

    report = {
        "experiment": "Healthcare recovery policy simulation",
        "trials": TRIALS,
        "seed": SEED,
        "verification_statuses": summary[
            "verification_statuses"
        ],
        "baseline_retries": baseline_retries,
        "safeagent_retries": safeagent_retries,
        "retry_reduction_pct": round(
            retry_reduction_pct, 2
        ),
        "baseline_policy_unsafe_retries": unsafe_baseline,
        "safeagent_policy_unsafe_retries": unsafe_safeagent,
        "safeagent_stops": safeagent_counts["STOP"],
        "safeagent_escalations": safeagent_counts["ESCALATE"],
        "safeagent_decision_latency_ms": latency,
        "transaction_completion_rate": None,
        "actual_duplicate_submissions": None,
        "limitations": [
            "Synthetic policy inputs only",
            "No real payer integration",
            "No patient data",
            "No actual network failures in this experiment",
            "Transaction completion and duplicate rates not measured",
            "Latency measures local decision execution only",
            "Always-retry is a deliberately simple baseline",
        ],
    }

    csv_path = OUTPUT_DIR / "healthcare_trials.csv"

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys(),
        )
        writer.writeheader()
        writer.writerows(results)

    json_path = OUTPUT_DIR / "healthcare_summary.json"

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nHEALTHCARE EXPERIMENT ANALYSIS")
    print("=" * 50)

    print(f"Trials: {TRIALS}")
    print(f"Baseline retries: {baseline_retries}")
    print(f"SafeAgent retries: {safeagent_retries}")
    print(f"Retry reduction: {retry_reduction_pct:.2f}%")
    print(f"Baseline policy-unsafe retries: {unsafe_baseline}")
    print(f"SafeAgent policy-unsafe retries: {unsafe_safeagent}")
    print(f"SafeAgent STOP decisions: {safeagent_counts['STOP']}")
    print(
        f"SafeAgent ESCALATE decisions: "
        f"{safeagent_counts['ESCALATE']}"
    )

    print(
        f"Mean decision latency: "
        f"{latency['mean_ms']:.6f} ms"
    )

    print("\nTransaction completion: NOT MEASURED")
    print("Actual duplicate submissions: NOT MEASURED")

    print(f"\nResults saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()