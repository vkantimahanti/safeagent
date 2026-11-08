# SafeAgent: Research Methodology

## 1. Research Overview

SafeAgent is an experimental research framework investigating reliable and risk-aware execution of autonomous AI agents in enterprise workflows.

The research focuses on uncertain execution outcomes arising from API timeouts, communication failures, process interruptions, and repeated tool invocations.

The objective is to evaluate mechanisms that minimize duplicate operations, preserve system consistency, and support safe recovery decisions.

The initial research environment uses a simulated electricity utility service-request workflow.

The project follows an incremental experimental approach, beginning with deterministic execution baselines and progressing toward controlled failure injection, recovery-policy comparisons, and AI agent orchestration.

## 2. Research Problem

Enterprise AI agents increasingly interact with external systems through APIs and automated tools.

Unlike read-only operations, state-changing actions can produce unintended consequences when repeated.

For example, an AI agent may successfully create a utility service ticket but fail to receive confirmation because of a communication timeout.

The agent must determine whether to retry the operation, verify its previous outcome, or request additional intervention.

Unconditional retries may produce duplicate records, while avoiding retries entirely may leave workflows incomplete.

SafeAgent investigates recovery mechanisms for these uncertain execution scenarios.

The research distinguishes between three important concepts:

* **Logical operation:** An intended business action, such as creating one service ticket.
* **Operation identifier:** A stable identifier used to recognize repeated attempts to perform the same logical operation.
* **Business record identifier:** An identifier assigned to the resulting record, such as a service ticket ID.

A single logical operation may involve multiple execution attempts but should produce only the intended business outcome.

## 3. Research Questions

### RQ1: Duplicate Operations

How frequently do repeated state-changing operations create duplicate records when idempotency protection is absent?

### RQ2: Idempotent Execution

To what extent can operation identifiers and idempotency controls prevent duplicate business operations?

### RQ3: Recovery Under Uncertainty

How do different recovery strategies perform when an operation succeeds but its acknowledgment is lost?

### RQ4: Risk-Aware Recovery

Can a recovery policy incorporating execution evidence, operation risk, and authorization state improve reliability compared with conventional recovery approaches?

## 4. Research Hypotheses

**H1:** Repeated execution of a non-idempotent ticket-creation operation produces duplicate records.

**H2:** Idempotency-aware execution reduces duplicate records for repeated requests sharing the same logical operation identifier.

**H3:** Verification-based recovery avoids redundant execution when authoritative evidence confirms prior success; uncertain outcomes are escalated rather than automatically retried.

**H4 (prospective):** A risk-aware recovery policy may reduce unsafe actions while maintaining acceptable task-completion rates and execution overhead compared with specified baselines.

### Current Hypothesis Status

| Hypothesis | Evidence status | Relevant experiments |
| --- | --- | --- |
| H1 | Supported in deterministic baseline only | EXP-001 |
| H2 | Supported in tested sequential, threaded and SQLite-backed scenarios; no general distributed guarantee | EXP-002, EXP-003C, EXP-004 |
| H3 | Mechanism behavior supported by deterministic tests; comparative reduction in unsafe actions not yet quantified | EXP-003B, EXP-004D |
| H4 | Untested; prospective research hypothesis | EXP-006 |

The experiments establish controlled functional evidence, not statistical superiority, real-world reliability, or algorithmic novelty.

## 5. Experimental Environment

### 5.1 Application Domain

The initial application simulates an electricity utility service-request system.

Each request represents a customer-reported issue requiring a service ticket.

Example request:

* Customer ID: CUST-101
* Issue: Power outage
* Expected outcome: One service ticket per intended logical operation

All customer identifiers and service requests are synthetic.

### 5.2 Initial Implementation

The experimental environment is implemented using Python.

The current components include:

**UtilityService**

A simulated utility service that creates a new ticket for every request without checking whether the operation has previously been executed.

**IdempotentUtilityService**

An enhanced simulated utility service that associates operation identifiers with previously created tickets.

Repeated requests sharing the same operation identifier and request parameters return the original ticket.

Conflicting reuse of an operation identifier is rejected.

**ServiceTicket**

A data structure representing a service ticket, including its identifier, customer identifier, issue description, and status.

**In-Memory Storage**

Python dictionaries maintain ticket records and, for the idempotent implementation, operation-to-ticket mappings.

**Experimental Scripts**

Independent scripts execute the naive and idempotency-aware workflows.

**Automated Tests**

Pytest validates the expected behavior of the simulated services.

The original baseline uses in-memory storage. Subsequent experiments add controlled thread concurrency, SQLite transactional persistence, multiprocess execution, and initial HTTP endpoints. Autonomous AI agent orchestration and real network-failure injection have not been evaluated.

### 5.3 Implemented Extensions and Planned Capabilities

**Implemented:** deterministic post-execution acknowledgment-loss injection; verification/recovery decision controller; thread-level race demonstration; SQLite transactional ticket and operation records; two-process shared-database test; persistent operation lookup; initial FastAPI health and root endpoints.

**Not yet evaluated:** real network faults, abrupt process crashes, authenticated/authorized HTTP tool execution, autonomous agent orchestration, container orchestration, sustained benchmarks, and cross-system replication.

### 5.4 Software and Evidence Provenance

Observed development environment: Windows, Python 3.12.7, SQLite 3.45.3, pytest 9.2.0; for EXP-005, FastAPI 0.162.2, Uvicorn 0.54.0, HTTPX 0.28.1. These are observed versions, not a fully pinned reproducible lockfile. Repository source and tests are the primary executable evidence. Results in this document refer to the specific tests and demonstrations described; they should not be interpreted as independent replication.

## 6. Experimental Design

### EXP-001: Naive Retry Baseline

**Status:** Completed

#### Objective

Demonstrate the effect of repeated state-changing operations without idempotency protection.

#### Hypothesis

Repeated execution of the same logical ticket-creation operation will produce duplicate service tickets.

#### Implementation

The experiment uses `UtilityService`, which creates a new service ticket for each invocation.

The service does not associate requests with logical operation identifiers.

#### Experimental Procedure

1. Initialize an empty `UtilityService` instance.
2. Submit a service-ticket creation request.
3. Repeat the same request.
4. Retrieve all created tickets.
5. Compare the number of tickets with the intended number of logical requests.

#### Experimental Configuration

| Parameter                   | Value                       |
| --------------------------- | --------------------------- |
| Customer ID                 | CUST-101                    |
| Issue                       | Power outage                |
| Intended logical operations | 1                           |
| Initial execution attempts  | 1                           |
| Additional retries          | 1                           |
| Total invocations           | 2                           |
| Storage                     | In-memory Python dictionary |
| Execution                   | Sequential, single-process  |

#### Observed Results

| Measurement                 | Result |
| --------------------------- | ------ |
| First ticket                | T-1001 |
| Retry ticket                | T-1002 |
| Total tickets created       | 2      |
| Intended logical operations | 1      |
| Duplicate tickets           | 1      |

#### Conclusion

The naive implementation creates a new ticket for every invocation, even when the caller intends to repeat the same logical operation.

This demonstrates the absence of idempotency protection.

The experiment establishes deterministic baseline behavior. It does not simulate an actual network failure.

#### Reproducibility

**Service implementation:**

`src/safeagent/services/utility_service.py`

**Experiment:**

`experiments/baselines/naive_retry.py`

**Automated test:**

`tests/test_utility_service.py`

**Execution command:**

```bash
python experiments/baselines/naive_retry.py
```

---

### EXP-002: Idempotency-Aware Execution

**Status:** Completed — Initial Sequential Evaluation

#### Objective

Evaluate whether stable operation identifiers prevent duplicate service-ticket creation when the same logical operation is executed multiple times.

#### Hypothesis

Repeated requests sharing the same operation identifier will return the original service ticket without creating additional records.

#### Implementation

The experiment implements an `IdempotentUtilityService` using Python and an in-memory operation registry.

Each operation identifier is associated with its original request parameters and resulting service ticket.

The implementation supports:

1. Creating a ticket for a new operation identifier.
2. Returning the original ticket for repeated requests using the same identifier.
3. Creating independent tickets for different operation identifiers.
4. Rejecting conflicting reuse of an operation identifier.
5. Rejecting empty operation identifiers.

The operation identifier is supplied by the calling application.

For the controlled experiment, identifiers such as `OP-101` and `OP-102` are assigned explicitly.

In a future agent-based implementation, operation identifiers may be generated programmatically and persisted with the workflow state.

#### Experimental Procedure

1. Initialize an empty `IdempotentUtilityService`.
2. Submit a ticket-creation request using operation ID `OP-101`.
3. Repeat the request using `OP-101`.
4. Submit an independent request using `OP-102`.
5. Retrieve the created tickets.
6. Verify the ticket identifiers and total ticket count.
7. Execute the automated test suite.

#### Experimental Configuration

| Parameter                | Value                         |
| ------------------------ | ----------------------------- |
| Customer ID              | CUST-101                      |
| Issue                    | Power outage                  |
| Initial Operation ID     | OP-101                        |
| Retry Operation ID       | OP-101                        |
| Independent Operation ID | OP-102                        |
| Storage                  | In-memory Python dictionaries |
| Execution                | Sequential, single-process    |

#### Observed Results

| Measurement                    | Result |
| ------------------------------ | ------ |
| First ticket                   | T-1001 |
| Retry ticket                   | T-1001 |
| Independent request ticket     | T-1002 |
| Total service invocations      | 3      |
| Unique logical operations      | 2      |
| Tickets created                | 2      |
| Duplicate tickets              | 0      |
| Retry returned original ticket | True   |

#### Automated Test Results

The complete test suite was executed using pytest.

| Measurement          | Result       |
| -------------------- | ------------ |
| Total tests executed | 5            |
| Tests passed         | 5            |
| Tests failed         | 0            |
| Execution time       | 0.06 seconds |

The test suite includes one naive baseline test and four idempotency-related tests.

The tests verify:

1. Repeated requests using the same operation identifier return the original ticket.
2. Different operation identifiers create independent tickets.
3. Conflicting reuse of an operation identifier raises an error.
4. Empty operation identifiers are rejected.

#### Comparison with EXP-001

The following comparison considers one logical operation submitted twice.

| Metric             | EXP-001: Naive | EXP-002: Idempotent |
| ------------------ | -------------- | ------------------- |
| Logical operations | 1              | 1                   |
| Execution attempts | 2              | 2                   |
| Tickets created    | 2              | 1                   |
| Duplicate tickets  | 1              | 0                   |

The comparison demonstrates the expected benefit of idempotency protection under sequential execution.

#### Conclusion

The initial experiment supports the hypothesis that stable operation identifiers prevent duplicate ticket creation in the implemented single-process, in-memory environment.

Repeated requests using the same operation identifier return the original ticket, while independent requests create new tickets.

These findings demonstrate an established idempotency technique rather than a novel recovery mechanism.

#### Limitations

* No concurrent request execution.
* No persistent database.
* Operation history is lost when the service restarts.
* No simulated network timeout or acknowledgment loss.
* No distributed execution.
* No LLM-based agent integration.
* No statistical benchmarking or production-scale evaluation.

#### Reproducibility

**Service implementation:**

`src/safeagent/services/idempotent_utility_service.py`

**Experiment:**

`experiments/baselines/idempotent_retry.py`

**Automated tests:**

`tests/test_idempotent_utility_service.py`

**Execute experiment:**

```bash
python experiments/baselines/idempotent_retry.py
```

**Execute tests:**

```bash
python -m pytest -v
```

---

### EXP-003: Uncertain Execution Outcomes

**Status:** Completed for EXP-003A, EXP-003B and EXP-003C

#### Objective

Evaluate recovery behavior when a ticket is successfully created but its acknowledgment is lost.

#### Research Problem

An operation may complete successfully even when the calling application does not receive a successful response.

This creates uncertainty about whether the operation should be retried.

#### Failure Scenarios (implemented and prospective)

1. Failure before commit: transaction rollback tested in EXP-004B, not a network failure.
2. Failure after commit but before acknowledgment: simulated in EXP-003A and EXP-004D.
3. Delayed API response: not yet evaluated.
4. Repeated requests after a simulated timeout: evaluated in EXP-003A.

#### Recovery Strategies

**Strategy A: Unconditional Retry**

The caller retries the operation without verifying whether the previous attempt succeeded.

**Strategy B: Idempotency-Aware Retry**

The caller retries using the original operation identifier.

**Strategy C: Verification-Based Recovery**

The caller attempts to determine the previous operation's outcome before deciding whether another execution attempt is necessary.

#### Evaluation

Evaluation dimensions include:

* Duplicate operation rate.
* Task completion rate.
* Recovery success rate.
* Recovery latency.
* Additional execution attempts.

Current results are deterministic functional checks. Comparative latency, workload-scale metrics, and statistical analysis remain prospective.


#### EXP-003A: Lost Acknowledgment Simulation

**Status:** Completed — Initial Sequential Evaluation

**Objective**

Evaluate how naive and idempotency-aware retries behave when a ticket is successfully created but its acknowledgment is lost.

**Implementation**

A controlled failure injector executes the ticket-creation operation and then raises a simulated `TimeoutError` before returning the result.

The experiment compares two recovery strategies:

1. Naive retry without idempotency protection.
2. Idempotency-aware retry using the original operation identifier.

**Observed Results**

| Metric                         | Naive Retry | Idempotent Retry |
| ------------------------------ | ----------- | ---------------- |
| Intended logical operations    | 1           | 1                |
| Execution attempts             | 2           | 2                |
| Simulated lost acknowledgments | 1           | 1                |
| Tickets created                | 2           | 1                |
| Duplicate tickets              | 1           | 0                |
| Retry ticket                   | T-1002      | T-1001           |

**Automated Tests**

* Total tests: 8
* Passed: 8
* Failed: 0
* Execution time: 0.09 seconds

**Findings**

The experiment confirmed that a simulated acknowledgment loss can cause the caller to observe a timeout even though the business operation succeeded.

Naive retry created a duplicate ticket.

Idempotency-aware retry returned the original ticket without creating an additional record.

**Limitations**

* Single-process, sequential execution.
* In-memory storage.
* No actual HTTP communication.
* No concurrent requests.
* No persistent operation history.
* No statistical performance evaluation.

**Reproducibility**

Experiment:

`experiments/recovery/lost_acknowledgment.py`

Tests:

`tests/test_acknowledgment_loss.py`

Run:

```bash
python experiments/recovery/lost_acknowledgment.py
python -m pytest -v
```

**Conclusion**

EXP-003A demonstrates that idempotency-aware retry prevents duplicate ticket creation following simulated acknowledgment loss in the implemented environment.

---

#### EXP-003B: Verification-Based Recovery

**Status:** Completed — deterministic functional evaluation

**Objective.** Determine whether checking operation state before retrying can prevent a redundant action following an uncertain acknowledgment.

**Implementation.** `VerificationRecoveryController` maps `VerificationStatus` to `RecoveryDecision`. `ServiceStateVerifier` looks up a ticket by operation identifier using `get_ticket_by_operation`.

| Verification state | Controller decision | Interpretation |
| --- | --- | --- |
| `SUCCESS` | `STOP` | Existing operation is confirmed; do not execute again |
| `NOT_EXECUTED` | `RETRY` | Only authoritative proof of non-execution can permit a retry decision; separate policy/authorization checks still apply |
| `UNKNOWN` | `ESCALATE` | Evidence is insufficient; no automatic retry |

Verifier exceptions and unrecognized statuses also result in `ESCALATE`. Importantly, a missing registry entry is treated as `UNKNOWN`, **not** proof of non-execution.

**Procedure.** Test the three state mappings, error handling, and service lookup after simulated acknowledgment loss. Compare the resulting controller decision with the expected safety rule.

**Observed evidence.** The tests passed for successful-operation stopping, authoritative non-execution retry decision, unknown-outcome escalation, verifier exceptions, and unrecognized statuses. After simulated lost acknowledgment, the service verifier located the ticket and returned `SUCCESS`, leading to `STOP`.

**Evidence:** `src/safeagent/recovery/verification.py`; `src/safeagent/recovery/service_verifier.py`; `tests/test_verification_recovery.py`; `tests/test_service_state_verification.py`.

**Limitations.** This is a decision-policy test, not an end-to-end authorization engine or measured comparison of production recovery strategies. The initial verifier used in-memory state.

#### EXP-003C: Thread-Level Concurrency and Check-Then-Act Races

**Status:** Completed — controlled two-thread evaluation

**Objective.** Test whether a non-atomic lookup-then-create sequence can violate idempotency under simultaneous requests.

**Procedure.** Run two threads with the same logical operation identifier. Use `threading.Barrier(2)` to reproduce the unsafe interleaving. Compare with a lock-protected implementation that guards the complete check-and-create critical section.

| Measurement | Unsafe check-then-act | Shared-lock protection |
| --- | ---: | ---: |
| Concurrent requests | 2 | 2 |
| Tickets created | 2 | 1 |
| Unintended duplicate tickets | 1 | 0 |

**Interpretation.** The observed race demonstrates why a sequential idempotency test does not establish concurrent safety. A shared process lock protected this particular critical section.

**Evidence:** `experiments/recovery/concurrent_idempotency.py`; `tests/test_concurrent_idempotency.py`.

**Limitations.** A Python lock does not coordinate independent processes or hosts. The two-thread setup is a deterministic counterexample, not a throughput benchmark.

---

### EXP-004: Persistent Idempotency and Recovery

**Status:** Completed — tested local SQLite scenarios

**Objective.** Evaluate whether transactional storage preserves one committed ticket per logical operation across service-object reinitialization, independent processes, and simulated acknowledgment loss.

#### EXP-004A: Database Initialization

**Implementation.** `initialize_database(db_path)` creates the parent directory and two SQLite tables: `tickets` (autoincrement ticket key, customer, issue, status) and `operations` (unique operation ID, unique ticket reference, original request fields, foreign key to tickets).

**Invariant.** A committed operation identifier must resolve to its corresponding committed ticket. A unique operation ID must not map to multiple committed tickets.

**Evidence:** `src/safeagent/services/database.py`; database-backed service tests.

#### EXP-004B: Transactional Ticket Creation

**Implementation.** `PersistentUtilityService.create_ticket(customer_id, issue, operation_id)` validates the operation ID, opens a SQLite connection, enables foreign-key enforcement, and starts `BEGIN IMMEDIATE`. Within one transaction it either returns the existing ticket for a matching operation/payload, rejects conflicting payload reuse, or inserts both ticket and operation mapping before commit. An error before commit rolls back both changes.

**Test conditions.** First creation; identical retry; different service instance against the same database; conflicting payload; blank operation ID; deliberate failure of operation registration using a SQLite trigger.

**Observed evidence.** Matching retries returned the original ticket; conflicting payloads were rejected; data remained accessible after service-object reinitialization; the injected registration failure did not leave a partially committed ticket.

**Evidence:** `src/safeagent/services/persistent_utility_service.py`; `tests/test_persistent_utility_service.py`.

**Implementation note.** On Windows, a temporary database could not be deleted while a SQLite connection remained open. The implementation was corrected to explicitly close connections with `contextlib.closing`; SQLite's connection transaction context manager alone does not close the connection.

#### EXP-004C: Multiprocess Idempotency

**Procedure.** Two independent Python processes use a shared SQLite database and submit the same operation ID. `BEGIN IMMEDIATE` coordinates writers; uniqueness constraints protect the operation mapping.

**Observed evidence.** The test verified one stored ticket and the same ticket ID returned to both processes (observed `T-1` in the controlled run).

**Evidence:** `tests/test_multiprocess_idempotency.py`; `src/safeagent/services/persistent_utility_service.py`.

**Limitations.** Two local processes, one SQLite file, one controlled scenario. No sustained contention, crash injection, or distributed database deployment.

#### EXP-004D: Persistent Acknowledgment Recovery

**Procedure.** Commit ticket creation; inject `TimeoutError` after the side effect; instantiate a new service object against the same SQLite file; verify the operation; apply the recovery decision controller.

**Observed evidence.** Committed operation was found, verification returned `SUCCESS`, and the controller returned `STOP`. The test found no duplicate ticket.

**Evidence:** `tests/test_persistent_acknowledgment_recovery.py`; `src/safeagent/faults/acknowledgment_loss.py`; `src/safeagent/recovery/service_verifier.py`.

**Limitations.** A new service object is not the same as a forcibly terminated OS process. The timeout is a Python simulation, not a dropped HTTP response.

**EXP-004 conclusion.** SQLite transactions, unique operation identifiers, and persistent verification provided the expected idempotency and recovery behavior in the evaluated scenarios. This is established engineering practice tested in a constrained environment, not evidence of a new distributed transaction protocol.

---

### EXP-005: HTTP-Based Tool Execution

**Status:** In progress — initial endpoints implemented; ticket-creation API not yet evaluated

**Objective.** Introduce an HTTP boundary so subsequent experiments can investigate client/server acknowledgment loss, operation verification, and recovery without conflating them with direct in-process method calls.

**Implemented:** `GET /health` returns HTTP 200 with `{"status": "healthy", "service": "safeagent"}`. `GET /` returns a welcome payload. Both passed dedicated FastAPI `TestClient` tests.

**Planned:** `POST /tickets` backed by `PersistentUtilityService`; `GET /operations/{operation_id}`; request validation; conflict handling; isolated integration-test database; real HTTP fault injection; process restart scenarios.

**Evidence:** `src/safeagent/api/main.py`; `tests/test_api_health.py`.

**Current test status.** The existing suite was observed to collect 29 passing tests; the two API tests passed in a separate run. A combined 31-test run has not been evidenced in the supplied record.

**Limitations.** A successful HTTP health response does not validate HTTP ticket execution, fault recovery, or agent integration.

---

### EXP-006: Risk-Aware Recovery

**Status:** Planned — research hypothesis not yet evaluated

**Objective.** Investigate whether recovery decisions should additionally consider operation impact, reversibility, authorization validity, and the strength of execution evidence.

**Candidate inputs:** state-changing versus read-only operation; reversibility; available idempotency guarantees; evidence provenance; authorization freshness; expected harm from duplicate or omitted execution.

**Proposed baselines:** unconditional retry, idempotency-aware retry, and verification-based recovery.

**Proposed outcomes:** unsafe action rate, duplicate operation rate, task completion, recovery success, latency, and overhead.

**Pre-registration requirements before testing:** define risk classes and policy rules, specify comparable workloads and fault distributions, establish baselines and safety oracles, run repeated trials, and report uncertainty intervals and adverse cases.

No novelty, safety improvement, or performance claim is made for EXP-006 at this stage.

---

## 7. Evaluation Metrics

Metrics are **defined here**, but most have **not yet been measured across a statistically meaningful workload**.

| Metric | Operational definition | Current evidence |
| --- | --- | --- |
| Duplicate operation rate | `(committed business outcomes − intended successful logical outcomes, floored at zero) / intended logical operations` for a specified workload | Deterministic counts in EXP-001–004 |
| Task completion rate | `logical workflows meeting predefined success criteria / attempted logical workflows` | Not benchmarked |
| Recovery success rate | `injected failure cases ending in correct verified outcome / injected failure cases` | Individual functional scenarios only |
| Recovery latency | Time from failure detection to verified recovery or terminal decision | Not benchmarked |
| Unsafe action rate | `state-changing attempts violating a predefined safety rule / total state-changing attempts` | Not benchmarked |
| Execution overhead | Extra API calls, verification requests, database operations, processing time, or resource use relative to a matched baseline | Not benchmarked |

A **logical operation** must be identified independently of the number of attempts. For comparative studies, specify denominators, timeout boundaries, handling of unknown outcomes, trial counts, confidence intervals, and the ground-truth oracle before execution. Do not treat passing unit tests as statistical estimates.

## 8. Reproducibility and Evidence Management

### 8.1 Repository and installation

SafeAgent uses a `src/` Python package layout and version-controlled tests. From the project root:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -v
```

`pyproject.toml` defines the package and pytest development dependency. FastAPI/Uvicorn/HTTPX were installed for EXP-005; dependency declarations and a pinned environment snapshot should be verified before public benchmark release.

### 8.2 Reproduction entry points

Confirmed script paths from the project record:

```powershell
python experiments/baselines/naive_retry.py
python experiments/baselines/idempotent_retry.py
python experiments/recovery/lost_acknowledgment.py
python experiments/recovery/concurrent_idempotency.py
```

Other EXP-003/004 behaviors are reproducible through their corresponding pytest modules. Run from the project root:

```powershell
python -m pytest tests/test_verification_recovery.py tests/test_service_state_verification.py -v
python -m pytest tests/test_concurrent_idempotency.py -v
python -m pytest tests/test_persistent_utility_service.py -v
python -m pytest tests/test_multiprocess_idempotency.py -v
python -m pytest tests/test_persistent_acknowledgment_recovery.py -v
python -m pytest tests/test_api_health.py -v
```

### 8.3 Evidence retention protocol

For each experiment, retain: hypothesis; exact code revision/commit hash; environment and dependency versions; input and fault configuration; command executed; raw test or trace output; outcome table; known failures; limitations; and changes made after observing results.

The companion `docs/research_journal.md` records observations and implementation decisions separately from planned methodology. Commit hashes, timestamps for every trial, and raw machine-readable result artifacts remain to be added.

### 8.4 Repeatability and statistical rigor

The current tests establish deterministic behavior, not statistical significance. Before making comparative performance or reliability claims, use repeated trials, representative workloads, controlled random seeds where applicable, confidence intervals, and predeclared success criteria. Document failed trials and exclusions rather than selectively reporting successes.

## 9. Threats to Validity

1. **Construct validity:** Ticket duplication is a narrow proxy for broader safety. Define business harm and policy violations independently for future risk-aware evaluations.
2. **Internal validity:** Fault injection occurs inside Python and may not model the timing or ambiguity of real network faults.
3. **Concurrency validity:** The thread race and two-process SQLite test demonstrate limited interleavings, not correctness under arbitrary schedules or high load.
4. **Durability validity:** Service-object reinitialization and committed SQLite writes do not establish survival under power loss, disk failure, or forced process termination.
5. **External validity:** Synthetic utility-ticket requests do not establish transferability to healthcare, payments, or other regulated domains.
6. **Agent validity:** No autonomous LLM agent has yet selected tools or decided on retries in the reported experiments.
7. **Measurement validity:** Functional test pass counts do not estimate operational error rates, latency distributions, or statistical effect sizes.
8. **Reproducibility gaps:** The public benchmark requires pinned dependencies, raw outputs, commit-linked runs, and documented platform-specific behavior.

**Mitigations planned:** real HTTP failure injection; process-crash tests; multiworker contention; alternative storage backends; independent safety oracles; repeated trials; agent integration; and external replication.

## 10. Research Status and Interpretation

| Experiment | Focus | Status |
| --- | --- | --- |
| EXP-001 | Naive retry | Completed |
| EXP-002 | Sequential in-memory idempotency | Completed |
| EXP-003A | Simulated acknowledgment loss | Completed |
| EXP-003B | Verification-based recovery | Completed |
| EXP-003C | Thread-level race | Completed |
| EXP-004A | SQLite schema | Completed |
| EXP-004B | Transactional idempotency | Completed |
| EXP-004C | Two-process shared SQLite | Completed |
| EXP-004D | Persistent acknowledgment recovery | Completed |
| EXP-005 | HTTP integration | In progress |
| EXP-006 | Risk-aware recovery | Planned |

### 10.1 Supported findings

Naive retries duplicated a ticket in the deterministic baseline; stable operation IDs prevented duplicates in tested sequential paths; a controlled race defeated an unsafe check-then-act pattern; shared locking protected the tested thread path; SQLite transactions preserved operation mappings across service-object reinitialization and the tested two-process run; persistent lookup after simulated acknowledgment loss supported a `STOP` decision.

### 10.2 Not established

The current evidence does **not** demonstrate a novel risk-aware algorithm, a production-safe AI agent, end-to-end network-failure resilience, generalized distributed exactly-once execution, statistically significant improvement over existing systems, or external scientific validation.

### 10.3 Next phase and publication readiness

Complete HTTP ticket and verification endpoints; run fault-injected end-to-end tests; capture repeatable baseline comparisons and uncertainty estimates; then formulate and test a distinctive risk-aware policy against established methods. For a credible public research artifact, pair source code with commit-linked experimental logs, versioned data/configuration, a literature review, an explicit contribution statement, and independent review or replication.

**Research-integrity note:** Technical documentation and open-source experiments can provide evidence of original technical work, but they do not by themselves establish eligibility under any immigration category or prove recognized scholarly impact. Any future EB-1A submission should rely on authentic, independently verifiable contributions and recognition.



---

# 11. Research Methodology Update — EXP-005 through EXP-007 (2026-11-08)

> **Status precedence:** This section supersedes outdated *status* statements in Sections 5–10, while preserving their original procedures and observations. In particular, the earlier description of EXP-005 as health-only, and EXP-006 as the planned risk-aware experiment, are historical. Current numbering uses **EXP-006 for quantitative benchmarks** and **EXP-007 for risk-aware policy**.

## 11.1 Scope and current implementation

SafeAgent now includes an HTTP API (`GET /health`, `GET /`, `POST /tickets`, `GET /operations/{operation_id}`), a SQLite-backed idempotent ticket service, synchronous and asynchronous recovery clients, controlled HTTPX transport fault injection, and an initial risk-aware decision controller. The HTTP API uses Pydantic request/response validation, HTTP 409 for conflicting reuse of an operation ID, and HTTP 422 for invalid request payloads. An unknown operation lookup returns `UNKNOWN`, **not** `NOT_EXECUTED`.

The currently implemented risk-aware controller is a deterministic policy; no LLM-powered agent or LangGraph orchestration has yet been verified. `EXP-007B` (trusted operation registry using Pydantic) has been specified but its test result has not been reported.

## 11.2 EXP-005 — HTTP tool execution and recovery (completed in controlled tests)

| Sub-experiment | Experimental condition | Observed/confirmed scope |
| --- | --- | --- |
| 005A–C | Health/root, ticket POST, operation verification GET | API tests passed; same-ID replay returns original ticket; conflicting payload rejected; unknown lookup is UNKNOWN |
| 005D–F | Simulated missing POST acknowledgment and recovery client | Verified committed operation leads to STOP; unknown outcome leads to ESCALATE; controller returns `RecoveryResult.decision` |
| 005G–H | `HTTPAcknowledgmentLossTransport` raises `httpx.ReadTimeout` **after** ASGI response is produced | HTTP client sees timeout while SQLite contains committed ticket; asynchronous verification can return STOP |
| 005I | POST acknowledgment loss followed by verification GET failure | Conservative ESCALATE; committed ticket remains single |
| 005J | Service-object reinitialization against same SQLite file | Committed operation found and STOP selected |
| 005K | Clean exit of one Python process and recovery in a fresh process | Persistent state verified after process change; **not** a crash/power-loss test |

Transport failures are injected inside an HTTPX/ASGI test harness. They do not establish behavior under actual packet loss, TLS failures, remote server crashes, or network partitions. A cleanly restarted service is not an abruptly killed process.

**Key evidence paths:** `src/safeagent/api/main.py`, `src/safeagent/api/models.py`, `src/safeagent/api/dependencies.py`, `src/safeagent/recovery/http_client.py`, `src/safeagent/recovery/async_http_client.py`, `src/safeagent/faults/http_acknowledgment_loss.py`, `tests/test_http_transport_failure.py`, `tests/test_http_verification_failure.py`, `tests/test_api_service_restart.py`, and `tests/test_process_restart_recovery.py`.

## 11.3 EXP-006 — Quantitative and concurrency benchmarks

| Experiment | Design | Observed results and interpretation |
| --- | --- | --- |
| 006A | 100 independent naive trials and 100 in-memory idempotent trials; two attempts per logical operation | Naive duplicate rate **100%**, idempotent **0%**. Mean operation times reported **0.0033 ms** and **0.0027 ms**, respectively. Deterministic toy workload; not production rates. |
| 006B | 100 trials per strategy, comparing naive, in-memory idempotent, SQLite persistent | Mean latency **0.0124 ms**, **0.0090 ms**, **7.1360 ms** respectively. Durability and measurement conditions differ; not a matched overhead estimate. |
| 006C | 10 trials each at 1, 2, 5, 10 workers against SQLite | Mean trial wall times **10.57**, **16.00**, **51.37**, **126.50 ms** respectively; 180 reported successful requests. Scheduling, initialization and SQLite contention may affect timing. |
| 006D | 10 threads synchronized before submitting same operation ID | One unique returned ticket ID; independently checked **1 committed ticket** and **1 operation**. SQLite file handles explicitly closed on Windows. |
| 006E | 5 asynchronous clients, each with post-response acknowledgment loss | Each recovered to STOP; independently checked 1 committed ticket and operation; in-process ASGI harness. |
| 006F | 5 asynchronous clients; 2 receive HTTP success and 3 simulated timeouts | Test passed; shared operation ID produced 1 committed ticket and operation, and timed-out clients verified STOP. |
| 006G | 100 trials for each of three deterministic scenarios | **300/300** expected recovery decisions. Scenario A SUCCESS→STOP; B verification timeout→ESCALATE; C missing lookup→ESCALATE. Mean recovery-phase latencies: **4.1316**, **0.2356**, **2.4436 ms**. Scenario B injects an immediate exception and does not model real timeout duration. |
| 006H | 100 trials per scenario; fixed seed 42; shuffled trial order; simulated 50 ms verification delay; client-workflow timing | User confirmed benchmark executed successfully; **numerical CSV output not reviewed**, so no latency or accuracy figures are claimed here. Scenario C omits POST and is not equivalent end-to-end work. |

**Raw artifacts / scripts:** `results/exp006a/duplicate_rate.csv`, `results/exp006g/recovery_reliability.csv`, `results/exp006h/reproducible_recovery.csv` (when retained); `experiments/benchmarks/duplicate_rate.py`, `persistent_latency.py`, `concurrent_workload.py`, `synchronized_concurrency.py`, `recovery_reliability.py`, and `reproducible_recovery.py`. The named result files are intended repository locations; their presence in a given Git commit must be verified.

**EXP-006G policy accuracy is not an independently estimated probability of real-world recovery success.** Expected decisions were derived from the same specified policy tested under deterministic faults. For statistical reliability claims, define an independent outcome oracle, randomized failures, matched baselines, and uncertainty intervals.

## 11.4 EXP-007 — Risk-aware policy

**EXP-007A (completed):** `src/safeagent/recovery/risk_aware.py` defines LOW/MEDIUM/HIGH operation risk and a controller combining risk with verified execution status. All **9 parameterized policy tests passed**; the full test suite subsequently reported **58 passing tests**.

| Verification state | LOW | MEDIUM | HIGH |
| --- | --- | --- | --- |
| `SUCCESS` | STOP | STOP | STOP |
| Authoritative `NOT_EXECUTED` | RETRY | RETRY | ESCALATE |
| `UNKNOWN` | ESCALATE | ESCALATE | ESCALATE |

The high-risk `NOT_EXECUTED` branch requires further authorization by policy. This is a *proposed* policy, not an empirically validated optimal risk rule. The `RETRY` decision is permission under the tested policy, not evidence that the service has already retried or that all necessary authorization checks are enforced.

**EXP-007B (specified, not confirmed):** An operation registry maps `READ_CUSTOMER`→LOW, `CREATE_TICKET`→MEDIUM, `DISCONNECT_POWER`→HIGH with authorization required for disconnection. Pydantic validates types and schema, but does not establish whether risk labels are ethically or operationally appropriate. Five tests were proposed; do not claim 63 total tests until execution is confirmed.

**EXP-007C/D (planned):** LangGraph-based agent workflow, followed by an LLM tool-selection agent. **EXP-008/009 (planned):** randomized agent failures, checkpoint/recovery behavior, process interruptions, and comparative evaluation. Project scope currently stops after EXP-009 for a research-readiness review.

## 11.5 Latest test and evidence status

- **Last confirmed full test suite:** **58 passed**, after EXP-007A.
- **EXP-007B:** implementation and tests proposed; passing result not confirmed.
- **EXP-006H:** successful execution reported; actual per-scenario latency values not yet independently reviewed.
- Tests establish correctness in specified environments; they do not establish safety guarantees, external validity, or novelty.

### Additional reproducibility controls recommended

1. Record commit SHA, timestamp, dependency versions, OS, SQLite settings, and exact command for every benchmark run.
2. Store raw CSV outputs and an analysis script that reproduces all tables and summary statistics.
3. Repeat each benchmark across multiple independent runs and report variability and confidence intervals.
4. Separate POST latency, verification latency, and full client-workflow latency; use consistent timing boundaries when comparing strategies.
5. Define independent ground-truth outcomes and a severity-weighted unsafe-action metric before evaluating risk-aware recovery.
6. Test forced termination, restart with persisted checkpoints, and failure before/after commit; do not conflate clean process exit with crash recovery.
7. Evaluate LangGraph baseline checkpointing separately from SafeAgent-specific policy contributions.

### Interpretation and research integrity

The implementation demonstrates known engineering methods—idempotency keys, transactional storage, verification before retry, conservative escalation—under increasingly varied controlled conditions. Distinct research novelty, improvement over established baselines, real-network fault tolerance, and production safety remain **unproven**. Research documentation is not itself evidence of scholarly recognition or immigration eligibility.
