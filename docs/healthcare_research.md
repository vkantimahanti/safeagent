# SafeAgent: Healthcare Recovery Research

## 1. Research Objective

Evaluate whether risk-aware, evidence-guided recovery reduces
policy-unsafe retry decisions in synthetic healthcare
administrative workflows.

## 2. Healthcare Workflow

The prototype models three administrative operations:

- CHECK_ELIGIBILITY — LOW risk
- SUBMIT_PRIOR_AUTH — MEDIUM risk
- CANCEL_PRIOR_AUTH — HIGH risk

The experiments primarily evaluate SUBMIT_PRIOR_AUTH.

No real patient data or payer systems are involved.

## 3. Recovery Policy

| Verification Status | LOW | MEDIUM | HIGH |
|---|---|---|---|
| SUCCESS | STOP | STOP | STOP |
| NOT_EXECUTED | RETRY | RETRY | ESCALATE |
| UNKNOWN | ESCALATE | ESCALATE | ESCALATE |

A missing database record is not considered authoritative
proof of non-execution.

## 4. Recovery Approaches

Four approaches were evaluated in a deterministic
post-commit acknowledgment-loss scenario:

1. Naive retry
2. Idempotency-only retry
3. Checkpoint-inspired retry with stable operation ID
4. SafeAgent verification-guided recovery

The checkpoint-inspired baseline does not implement actual
LangGraph checkpoint restoration.

## 5. Deterministic Comparison

| Approach | Authorizations | Retries | Duplicates |
|---|---:|---:|---:|
| Naive | 2 | 1 | 1 |
| Idempotent | 1 | 1 | 0 |
| Checkpoint + stable ID | 1 | 1 | 0 |
| SafeAgent | 1 | 0 | 0 |

These implementations differ in verification and persistence
mechanisms and are not equivalent end-to-end systems.

## 6. Process Crash Experiment

A Python process was terminated using os._exit(99)
after committing an authorization to SQLite.

A separate recovery process verified the existing record.

Observed result:

- Verification: SUCCESS
- Recovery decision: STOP
- Authorization count: 1

Recovery was manually initiated. Automatic workflow
resumption was not demonstrated.

## 7. Randomized Policy Experiment

- Trials: 1,000
- Seed: 42
- Operation risk: MEDIUM
- Verification statuses: SUCCESS, NOT_EXECUTED, UNKNOWN
- Baseline: Always retry
- SafeAgent: Risk-aware recovery controller

Verification statuses were sampled uniformly.

The experiment evaluates policy decisions rather than
actual healthcare transactions.

## 8. Metrics

Measured:

- Retry decisions
- STOP decisions
- ESCALATE decisions
- Policy-unsafe retry decisions
- Local recovery-decision latency

Not measured in the randomized experiment:

- Actual transaction completion rate
- Real-world duplicate submission rate
- Production system availability
- Patient safety outcomes
- End-to-end healthcare workflow latency

Policy-unsafe retry means retrying despite SUCCESS or
UNKNOWN verification status under the specified policy.

## 9. Experimental Artifacts

- results/healthcare/healthcare_trials.csv
- results/healthcare/healthcare_summary.json
- run_healthcare_analysis.py
- run_healthcare_comparison.py
- run_healthcare_crash.py

## 10. Limitations

1. Synthetic healthcare administrative workflows.
2. No real payer API integration.
3. No real patient information.
4. Simplified always-retry baseline.
5. Checkpoint-inspired baseline rather than actual
   checkpoint restoration.
6. Simulated authorization approval using a Boolean flag.
7. Randomized experiments exercise recovery-policy inputs,
   not actual distributed-system failures.
8. Decision latency excludes database, network, and
   orchestration overhead.
9. Results do not establish clinical or production safety.

## 11. Reproducibility

Run tests:

    python -m pytest tests/ -v

Run deterministic comparison:

    python run_healthcare_comparison.py

Run randomized analysis:

    python run_healthcare_analysis.py

Run process crash experiment:

    python run_healthcare_crash.py crash
    python run_healthcare_crash.py recover