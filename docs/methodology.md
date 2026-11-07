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

**H3:** Verification-based recovery reduces unnecessary repeated operations when execution outcomes are uncertain.

**H4:** Risk-aware recovery can reduce unsafe actions while maintaining acceptable task-completion rates and execution overhead.

### Current Hypothesis Status

| Hypothesis | Status                                         | Supporting Experiment |
| ---------- | ---------------------------------------------- | --------------------- |
| H1         | Supported in deterministic baseline            | EXP-001               |
| H2         | Initially supported under sequential execution | EXP-002               |
| H3         | Untested                                       | EXP-003 planned       |
| H4         | Untested                                       | EXP-004 planned       |

The initial experiments establish foundational behavior. They do not yet provide statistical evidence about performance under real-world operating conditions.

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

The current environment does not implement actual network communication, persistent storage, concurrency protection, or AI agent orchestration.

### 5.3 Planned Environment Extensions

Future experiments may introduce:

* HTTP-based API interactions.
* Persistent transactional storage.
* Controlled failure injection.
* Concurrent requests.
* AI agent orchestration.
* Execution tracing and observability.
* Containerized execution.
* Repeated benchmark workloads.

These extensions will be introduced incrementally and documented when implemented.

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

**Status:** Planned

#### Objective

Evaluate recovery behavior when a ticket is successfully created but its acknowledgment is lost.

#### Research Problem

An operation may complete successfully even when the calling application does not receive a successful response.

This creates uncertainty about whether the operation should be retried.

#### Proposed Failure Scenarios

1. Failure before the operation commits.
2. Failure after commit but before acknowledgment.
3. Delayed API response.
4. Repeated requests after a simulated timeout.

#### Proposed Recovery Strategies

**Strategy A: Unconditional Retry**

The caller retries the operation without verifying whether the previous attempt succeeded.

**Strategy B: Idempotency-Aware Retry**

The caller retries using the original operation identifier.

**Strategy C: Verification-Based Recovery**

The caller attempts to determine the previous operation's outcome before deciding whether another execution attempt is necessary.

#### Evaluation

The experiment will compare recovery strategies using metrics such as:

* Duplicate operation rate.
* Task completion rate.
* Recovery success rate.
* Recovery latency.
* Additional execution attempts.

Experimental parameters and fault-injection procedures will be finalized before implementation.

---

### EXP-004: Risk-Aware Recovery

**Status:** Planned

#### Objective

Evaluate a proposed recovery policy that considers operation risk, execution evidence, and authorization state.

#### Research Direction

The experiment will investigate whether recovery decisions can be improved by considering factors beyond retry availability.

Potential factors include:

* Whether the operation changes business state.
* Whether the operation is reversible.
* Whether an idempotency mechanism is available.
* Whether execution evidence indicates prior success.
* Whether authorization is still valid.
* Whether retrying could produce an unsafe business outcome.

#### Proposed Evaluation

The proposed mechanism will be compared against established recovery approaches.

Evaluation may consider:

* Unsafe action rate.
* Duplicate operation rate.
* Task completion rate.
* Recovery success rate.
* Recovery latency.
* Execution overhead.

The algorithm, baselines, and evaluation design will be documented after the research gap and implementation have been established.

No claims of novelty or performance improvement are made at this stage.

## 7. Evaluation Metrics

The following metrics are proposed for future comparative experiments.

### 7.1 Duplicate Operation Rate

**Definition:**

The number of unintended duplicate business operations relative to the number of intended logical operations.

**Formula:**

Duplicate Operation Rate = Duplicate business operations / Total intended logical operations

### 7.2 Task Completion Rate

**Definition:**

The proportion of attempted logical workflows that successfully achieve their intended business outcome.

**Formula:**

Task Completion Rate = Successfully completed logical workflows / Total attempted logical workflows

### 7.3 Recovery Success Rate

**Definition:**

The proportion of injected failure scenarios successfully recovered by the evaluated strategy.

**Formula:**

Recovery Success Rate = Successfully recovered failure scenarios / Total injected failure scenarios

### 7.4 Recovery Latency

**Definition:**

Elapsed time between failure detection and successful recovery or final termination.

**Measurement:**

Milliseconds or seconds.

### 7.5 Unsafe Action Rate

**Definition:**

The proportion of attempted state-changing operations that violate predefined safety policies.

**Formula:**

Unsafe Action Rate = Operations violating defined safety policies / Total attempted state-changing operations

### 7.6 Execution Overhead

**Definition:**

Additional resources required by a recovery strategy compared with the baseline.

Potential measurements include:

* Additional API calls.
* Processing time.
* Computational resources.
* Verification requests.
* Storage operations.

Metric definitions, measurement procedures, and statistical methods will be refined before comparative experiments.

## 8. Reproducibility

SafeAgent aims to maintain a reproducible experimental environment through:

1. Version-controlled source code.
2. Documented experiment configurations.
3. Automated tests.
4. Explicit software dependencies.
5. Repeatable execution commands.
6. Recorded experiment results.
7. Documented assumptions and limitations.

### 8.1 Installation

From the project root:

```bash
python -m pip install -e ".[dev]"
```

### 8.2 Execute EXP-001

```bash
python experiments/baselines/naive_retry.py
```

### 8.3 Execute EXP-002

```bash
python experiments/baselines/idempotent_retry.py
```

### 8.4 Run Automated Tests

```bash
python -m pytest -v
```

### 8.5 Research Journal

Experiment observations and implementation decisions are maintained in:

`docs/research_journal.md`

The research journal records observed results separately from the methodology.

### 8.6 Future Reproducibility Improvements

Future benchmark releases will record:

* Python and dependency versions.
* Experimental configuration files.
* Random seeds where applicable.
* Failure-injection parameters.
* Repeated trial results.
* Statistical uncertainty.
* Relevant execution logs and traces.

## 9. Threats to Validity

The initial experiments have several limitations.

### 9.1 Simulated Environment

The experiments use an in-memory utility service rather than a production enterprise system.

Results may differ when interacting with external APIs, databases, and distributed services.

### 9.2 No Network Failure Simulation

Actual API timeouts, lost acknowledgments, and communication failures have not yet been simulated.

### 9.3 No Concurrency Testing

The current idempotency implementation has not been evaluated under simultaneous requests.

Without synchronization or transactional storage, concurrent requests may create duplicate records.

### 9.4 No Persistent Storage

Operation history is lost when the application restarts.

The current implementation cannot guarantee idempotency across process restarts.

### 9.5 Limited Experimental Scale

The experiments demonstrate deterministic behavior using a small number of requests.

They do not establish statistically significant performance differences.

### 9.6 No AI Agent Integration

The initial experiments use direct Python method calls rather than autonomous AI agents.

Agent-specific behaviors, such as tool selection, planning, and repeated reasoning, have not yet been evaluated.

### 9.7 Limited Generalizability

Results from the simulated utility-ticket workflow cannot automatically be generalized to other enterprise systems.

Future experiments should consider additional state-changing operations and application domains.

### 9.8 Future Mitigation

Future research will address these limitations through:

* Controlled failure injection.
* Persistent transactional storage.
* Concurrent execution.
* Comparative recovery strategies.
* Agent orchestration.
* Repeated experimental trials.
* Explicit statistical evaluation.

## 10. Research Status

| Experiment | Description                  | Status                            |
| ---------- | ---------------------------- | --------------------------------- |
| EXP-001    | Naive retry baseline         | Completed                         |
| EXP-002    | Idempotency-aware execution  | Completed — Sequential Evaluation |
| EXP-003    | Uncertain execution outcomes | Planned                           |
| EXP-004    | Risk-aware recovery          | Planned                           |

### 10.1 Current Research Findings

**EXP-001:** Repeated ticket-creation requests without idempotency protection produce duplicate tickets in the deterministic baseline.

**EXP-002:** Stable operation identifiers prevent duplicate ticket creation during sequential retries in the implemented in-memory service.

These findings establish baseline behavior for future research.

They do not yet demonstrate a novel recovery mechanism.

### 10.2 Next Research Phase

EXP-003 will investigate uncertain execution outcomes, including scenarios in which a service operation succeeds but its acknowledgment is lost.

The experiment will compare recovery strategies using controlled failure injection and measurable reliability outcomes.

The objective is to establish stronger experimental evidence for evaluating recovery mechanisms under uncertainty.

### 10.3 Long-Term Research Direction

The longer-term goal is to investigate reliable and risk-aware execution mechanisms for AI agents operating in state-changing enterprise workflows.

Future research will focus on identifying and evaluating potential contributions that go beyond established idempotency and retry mechanisms.

Any claims regarding novelty, effectiveness, or generalizability will require appropriate literature review, controlled experiments, and independent validation.
