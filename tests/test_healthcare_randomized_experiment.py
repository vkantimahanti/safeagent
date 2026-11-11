from safeagent.healthcare.randomized_experiment import (
    run_randomized_healthcare_experiment,
    summarize_randomized_experiment,
)


def test_randomized_experiment_is_reproducible():
    first = run_randomized_healthcare_experiment(
        trials=1000,
        seed=42,
    )

    second = run_randomized_healthcare_experiment(
        trials=1000,
        seed=42,
    )

    assert first == second
    assert len(first) == 1000


def test_randomized_experiment_summary():
    results = run_randomized_healthcare_experiment(
        trials=1000,
        seed=42,
    )

    summary = summarize_randomized_experiment(results)

    assert summary["total_trials"] == 1000

    assert summary["baseline_decisions"]["RETRY"] == 1000

    assert (
        sum(summary["safeagent_decisions"].values())
        == 1000
    )

    assert set(summary["safeagent_decisions"]).issubset(
        {"STOP", "RETRY", "ESCALATE"}
    )