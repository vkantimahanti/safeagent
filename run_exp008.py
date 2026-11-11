from safeagent.experiments.randomized_failures import (
    run_randomized_experiment,
)

results = run_randomized_experiment(
    trials=1000,
    seed=42,
)

for (risk, status, decision), count in sorted(results.items()):
    print(
        f"Risk={risk:6} "
        f"Status={status:12} "
        f"Decision={decision:8} "
        f"Count={count}"
    )

print("Total trials:", sum(results.values()))