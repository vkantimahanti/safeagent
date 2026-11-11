from safeagent.experiments.exp010_benchmark import (
    run_benchmark,
    summarize_benchmark,
)


def main():
    rows = run_benchmark(
        trials=1000,
        seed=42,
        output_path="results/exp010_results.csv",
    )

    summary = summarize_benchmark(rows)

    print("\nEXP-010: Comparative Recovery Policy Benchmark")
    print("=" * 80)

    print(
        f"{'Approach':<22}"
        f"{'Retries':>10}"
        f"{'Escalations':>14}"
        f"{'Stops':>10}"
        f"{'Unsafe*':>12}"
    )

    print("-" * 80)

    for approach, metrics in summary.items():
        print(
            f"{approach:<22}"
            f"{metrics['retries']:>10}"
            f"{metrics['escalations']:>14}"
            f"{metrics['stops']:>10}"
            f"{metrics['policy_unsafe_retries']:>12}"
        )

    print("\n*Unsafe = violates our conservative recovery policy.")
    print("This does not imply actual harmful side effects.")

    print("\nResults saved to results/exp010_results.csv")


if __name__ == "__main__":
    main()