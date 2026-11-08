# SafeAgent

**A research framework for reliable and risk-aware AI-agent execution**

> **Research prototype — not production-ready.** The current implementation provides deterministic recovery policies, SQLite-backed idempotent service operations, an HTTP API, and controlled failure-injection experiments. **LangGraph and an LLM agent are planned, not yet implemented.**

## Research problem

When an API call times out, the caller may not know whether its state-changing operation committed. Blind retry may create duplicates; refusing to retry can leave work incomplete. SafeAgent studies operation identifiers, transactional persistence, verification-based recovery, and proposed risk-aware decisions in a synthetic electricity-utility service-request workflow.

## Research objectives

1. Prevent duplicate committed outcomes for repeated logical operations under explicitly tested conditions.
2. Distinguish confirmed success, authoritatively confirmed non-execution, and unknown outcomes.
3. Evaluate STOP, RETRY, and ESCALATE policies under controlled faults.
4. Measure duplicate rates, recovery-decision consistency, latency, concurrency behavior, and policy trade-offs.
5. Introduce LangGraph agent orchestration and evaluate agent-level recovery in later experiments.

## Current architecture

```text
Client / future AI agent
          |
          v
    FastAPI endpoints
   POST /tickets  GET /operations/{id}
          |
          v
PersistentUtilityService -- SQLite tickets + operations
          ^
          |
 HTTPX controlled fault injection
          |
          v
 Verification -> Recovery controller -> STOP / RETRY / ESCALATE
                        |
                 Risk-aware policy (EXP-007A)
```

The operation registry (EXP-007B), LangGraph workflow (EXP-007C), and LLM-powered agent (EXP-007D) are planned/under development and must not be represented as verified capabilities.

## Implemented functionality

- Naive and in-memory idempotent ticket services for baselines.
- SQLite-backed transactional ticket creation using stable operation IDs, `BEGIN IMMEDIATE`, uniqueness constraints, and payload-conflict detection.
- Verification of committed operations and conservative escalation for unknown outcomes.
- FastAPI endpoints: `GET /health`, `GET /`, `POST /tickets`, `GET /operations/{operation_id}`.
- Controlled acknowledgment-loss and verification-timeout injection using HTTPX ASGI transports.
- Recovery clients (synchronous and asynchronous) and initial risk-aware policy mapping.
- Automated tests, multiprocess scenarios, synchronized concurrency tests, and quantitative benchmark scripts.

## Current evidence

| Experiment | Confirmed observation |
| --- | --- |
| EXP-001 | Two naive attempts created two tickets for one logical operation. |
| EXP-002–003 | Stable operation ID prevented duplicates in sequential tests; verification policy chose STOP for success and ESCALATE for unknown. |
| EXP-004 | SQLite transactions preserved one committed mapping in tested rollback, service-reinitialization, and two-process scenarios. |
| EXP-005 | HTTP fault-injection and recovery tests passed in an in-process ASGI harness. |
| EXP-006A | 100 naive trials: 100% duplicate rate; 100 idempotent trials: 0%, in a deterministic constructed workload. |
| EXP-006D–F | Synchronized and mixed-outcome concurrency scenarios preserved one committed ticket/operation. |
| EXP-006G | 300/300 expected policy decisions in deterministic trials; **not** a production reliability estimate. |
| EXP-006H | Randomized/delayed benchmark completed by user report; numeric results have not been reviewed. |
| EXP-007A | Nine risk-aware policy tests passed; **58 total tests passed** in last confirmed full suite. |
| EXP-007B | Five tests proposed; result **not yet confirmed**. |

See [`docs/methodology.md`](docs/methodology.md) and [`docs/research_journal.md`](docs/research_journal.md) for the complete historical methodology and evidence log.

## Repository layout

```text
src/safeagent/              Service, API, recovery, and fault-injection code
experiments/baselines/      Initial baseline experiments
experiments/recovery/       Recovery and concurrency experiments
experiments/benchmarks/     Quantitative benchmark scripts
tests/                     Automated tests
docs/                      Methodology, journal, architecture, roadmap
results/                   Optional raw benchmark outputs (verify locally)
```

## Setup and tests

Use a supported Python environment (development runs reported Python 3.12.7):

```powershell
python -m pip install -e ".[dev]"
python -m pytest -v
```

If API/benchmark dependencies are not included in your local `pyproject.toml`, add and pin the versions you actually use before publishing a reproducible environment. Previously reported development versions include FastAPI 0.162.2, HTTPX 0.28.1, Uvicorn 0.54.0, and SQLite 3.45.3; confirm against your current environment.

## Run selected experiments

```powershell
python experiments/baselines/naive_retry.py
python experiments/baselines/idempotent_retry.py
python experiments/benchmarks/duplicate_rate.py
python experiments/benchmarks/recovery_reliability.py
python experiments/benchmarks/reproducible_recovery.py
```

## Recovery policy

| Verification | Default recovery | Risk-aware policy (EXP-007A) |
| --- | --- | --- |
| SUCCESS | STOP | STOP for all risk levels |
| Authoritative NOT_EXECUTED | RETRY | LOW/MEDIUM RETRY; HIGH ESCALATE |
| UNKNOWN | ESCALATE | ESCALATE for all risk levels |

A missing registry entry is **UNKNOWN**, not proof of non-execution. The controller's `RETRY` decision does not itself perform an external action or replace required authorization checks.

## Roadmap and scope

- **EXP-007B:** Trusted operation-risk registry; tests pending confirmation.
- **EXP-007C:** LangGraph orchestration of the execution/verification/recovery workflow.
- **EXP-007D:** LLM agent and tool selection with trusted policy boundaries.
- **EXP-008:** Randomized agent fault injection and baseline comparisons.
- **EXP-009:** Workflow interruption, persistence/checkpoints, and research-readiness review.

The planned project checkpoint is after EXP-009.

## Limitations and research integrity

The experiments use synthetic utility data, local SQLite, and mostly in-process or deterministic fault injection. They do not demonstrate real packet loss, distributed exactly-once execution, abrupt crash durability, production safety, or statistically significant superiority over existing frameworks. Idempotency and verification before retry are established techniques; the distinct contribution of SafeAgent remains to be tested. This repository does not control real utility infrastructure.

For full methodology, experiment caveats, evidence and debugging history, consult the documents in `docs/`.
