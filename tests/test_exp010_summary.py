from safeagent.experiments.exp010_benchmark import (
    run_benchmark,
    summarize_benchmark,
)


def test_exp010_summary(tmp_path):
    rows = run_benchmark(
        trials=1000,
        seed=42,
        output_path=str(tmp_path / "results.csv"),
    )

    summary = summarize_benchmark(rows)

    assert len(summary) == 4

    for approach in summary:
        assert summary[approach]["total"] == 1000

    assert summary["naive"]["retries"] == 1000
    assert summary["idempotent"]["retries"] == 1000
    assert summary["checkpoint_stable"]["retries"] == 1000

    assert summary["safeagent"]["policy_unsafe_retries"] == 0
    assert summary["safeagent"]["unnecessary_retries"] == 0

    for approach in summary:
        assert (
            summary[approach]["retries"]
            + summary[approach]["escalations"]
            + summary[approach]["stops"]
            == 1000
        )