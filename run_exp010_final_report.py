from pathlib import Path

from safeagent.experiments.end_to_end_comparison import (
    run_naive_post_commit_failure,
    run_idempotent_post_commit_failure,
    run_checkpoint_post_commit_failure,
    run_safeagent_post_commit_failure,
)
from safeagent.experiments.exp010_benchmark import (
    run_benchmark,
    summarize_benchmark,
)


def main():
    output_dir = Path("results/exp010_final")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Execute four approaches against the same simulated fault.
    results = [
        run_naive_post_commit_failure(),
        run_idempotent_post_commit_failure(
            str(output_dir / "idempotent.db")
        ),
        run_checkpoint_post_commit_failure(
            str(output_dir / "checkpoint.db")
        ),
        run_safeagent_post_commit_failure(
            str(output_dir / "safeagent.db")
        ),
    ]

    print("\nEXP-010: END-TO-END COMPARISON")
    print("=" * 75)

    print(
        f"{'Approach':<22}"
        f"{'Tickets':>10}"
        f"{'Retries':>10}"
        f"{'Duplicates':>13}"
    )

    print("-" * 75)

    for result in results:
        print(
            f"{result['approach']:<22}"
            f"{result['ticket_count']:>10}"
            f"{result['recovery_retries']:>10}"
            f"{result['duplicate_count']:>13}"
        )

    # Reproduce the policy benchmark.
    rows = run_benchmark(
        trials=1000,
        seed=42,
        output_path=str(output_dir / "policy_results.csv"),
    )

    summary = summarize_benchmark(rows)

    print("\nPOLICY BENCHMARK")
    print("=" * 75)

    for approach, metrics in summary.items():
        print(
            f"{approach:<22}"
            f"Retries={metrics['retries']:<5}"
            f"Escalations={metrics['escalations']:<5}"
            f"Stops={metrics['stops']:<5}"
        )

    print("\nResults saved under results/exp010_final/")


if __name__ == "__main__":
    main()