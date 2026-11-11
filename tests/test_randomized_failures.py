from safeagent.experiments.randomized_failures import (
    run_randomized_experiment,
)


def test_unknown_never_retries():
    results = run_randomized_experiment(
        trials=10000,
        seed=42,
    )

    unknown_count = 0

    for (risk, status, decision), count in results.items():

        if status == "UNKNOWN":
            unknown_count += count

            assert decision == "ESCALATE"

    assert unknown_count > 0


def test_high_risk_not_executed_never_retries():
    results = run_randomized_experiment(
        trials=10000,
        seed=42,
    )

    high_risk_count = 0

    for (risk, status, decision), count in results.items():

        if risk == "HIGH" and status == "NOT_EXECUTED":
            high_risk_count += count

            assert decision == "ESCALATE"

    assert high_risk_count > 0


def test_randomized_experiment_is_reproducible():
    first = run_randomized_experiment(
        trials=1000,
        seed=42,
    )

    second = run_randomized_experiment(
        trials=1000,
        seed=42,
    )

    assert first == second


def test_total_trial_count():
    trials = 10000

    results = run_randomized_experiment(
        trials=trials,
        seed=42,
    )

    assert sum(results.values()) == trials