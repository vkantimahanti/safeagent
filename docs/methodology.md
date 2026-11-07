# SafeAgent: Research Methodology

## 1. Research Overview

SafeAgent is an experimental research framework investigating reliable and risk-aware execution of autonomous AI agents in enterprise workflows.

The research focuses on uncertain execution outcomes arising from API timeouts, communication failures, process interruptions, and repeated tool invocations.

The objective is to evaluate mechanisms that minimize duplicate operations, preserve system consistency, and support safe recovery decisions.

The initial research environment uses a simulated electricity utility service-request workflow.

## 2. Research Problem

Enterprise AI agents increasingly interact with external systems through APIs and automated tools.

Unlike read-only operations, state-changing actions can produce unintended consequences when repeated.

For example, an AI agent may successfully create a utility service ticket but fail to receive the confirmation because of a communication timeout.

The agent must determine whether to retry the operation, verify its previous outcome, or request additional intervention.

Unconditional retries may produce duplicate records, while avoiding retries entirely may leave workflows incomplete.

SafeAgent investigates recovery mechanisms for these uncertain execution scenarios.

## 3. Research Questions

**RQ1: Duplicate Operations**

How frequently do repeated state-changing operations create duplicate records when idempotency protection is absent?

**RQ2: Idempotent Execution**

To what extent can operation identifiers and idempotency controls prevent duplicate business operations?

**RQ3: Recovery Under Uncertainty**

How do different recovery strategies perform when an operation succeeds but its acknowledgment is lost?

**RQ4: Risk-Aware Recovery**

Can a recovery policy incorporating execution evidence, operation risk, and authorization state improve reliability compared with conventional recovery approaches?

## 4. Research Hypotheses

**H1:** Repeated execution of a non-idempotent ticket-creation operation produces duplicate records.

**H2:** Idempotency-aware execution reduces duplicate records for repeated requests sharing the same logical operation identifier.

**H3:** Verification-based recovery reduces unnecessary repeated operations when execution outcomes are uncertain.

**H4:** Risk-aware recovery can reduce unsafe actions while maintaining acceptable task-completion rates and execution overhead.

H1 has been demonstrated in the initial deterministic baseline. H2–H4 remain untested.

## 5. Experimental Environment

### 5.1 Application Domain

The initial application simulates an electricity utility service-request system.

Each request represents a customer-reported issue requiring a service ticket.

Example request:

* Customer ID: CUST-101
* Issue: Power outage
* Expected outcome: One service ticket

All customer identifiers and service requests are synthetic.

### 5.2 Initial Implementation

The baseline is implemented using Python.

Components:

* UtilityService: Simulates service-ticket creation.
* ServiceTicket: Represents a ticket record.
* In-memory storage: Maintains created tickets.
* Baseline experiment: Executes repeated ticket-creation requests.
* Automated tests: Verify expected baseline behavior.

The current implementation does not include network communication, persistent storage, concurrency, or an AI agent.

### 5.3 Planned Environment Extensions

Future experiments will introduce:

* HTTP-based API interactions.
* Persistent storage.
* Controlled failure injection.
* Concurrent requests.
* AI agent orchestration.
* Execution tracing and observability.

These extensions have not yet been implemented.

## 6. Experimental Design

### EXP-001: Naive Retry Baseline

**Objective**

Demonstrate the effect of repeated state-changing operations without idempotency protection.

**Procedure**

1. Initialize an empty UtilityService instance.
2. Submit a service-ticket creation request.
3. Repeat the same request.
4. Retrieve all created tickets.
5. Compare the number of tickets with the intended number of logical requests.

**Input**

Customer ID: CUST-101

Issue: Power outage

Original requests: 1

Additional retries: 1

**Observed Results**

First ticket: T-1001

Second ticket: T-1002

Total tickets: 2

Duplicate tickets: 1

**Conclusion**

The baseline creates a new ticket for each invocation, demonstrating the absence of idempotency protection.

This experiment establishes deterministic baseline behavior. It does not simulate an actual network failure.

### EXP-002: Idempotency-Aware Execution (Planned)

**Objective**

Evaluate whether stable operation identifiers prevent duplicate ticket creation across repeated invocations.

**Proposed Procedure**

1. Generate a unique identifier for a logical service request.
2. Submit the request with the identifier.
3. Repeat the request using the same identifier.
4. Verify whether the original ticket is returned.
5. Submit a different logical request with a new identifier.
6. Verify that a new ticket is created.

**Expected Behavior**

Repeated requests sharing the same operation identifier should not create additional tickets.

Actual results will be documented after implementation.

### EXP-003: Uncertain Execution Outcomes (Planned)

**Objective**

Evaluate recovery behavior when a ticket is successfully created but its acknowledgment is lost.

**Proposed Failure Scenarios**

* Failure before the operation commits.
* Failure after commit but before acknowledgment.
* Delayed API response.
* Repeated requests after a simulated timeout.

**Evaluation**

Compare retry-only, idempotency-aware, and verification-based recovery strategies.

### EXP-004: Risk-Aware Recovery (Planned)

**Objective**

Evaluate a proposed recovery policy that considers operation risk, execution evidence, and authorization state.

The proposed mechanism will be compared against established recovery approaches.

The algorithm and evaluation design will be documented after the research gap and implementation have been established.

## 7. Evaluation Metrics

The following metrics are proposed for future comparative experiments.

### 7.1 Duplicate Operation Rate

Duplicate Operation Rate = Duplicate business operations / Total intended logical operations

### 7.2 Task Completion Rate

Task Completion Rate = Successfully completed logical workflows / Total attempted logical workflows

### 7.3 Recovery Success Rate

Recovery Success Rate = Successfully recovered failure scenarios / Total injected failure scenarios

### 7.4 Recovery Latency

Elapsed time between failure detection and successful recovery or final termination.

### 7.5 Unsafe Action Rate

Unsafe Action Rate = Operations violating defined safety policies / Total attempted state-changing operations

### 7.6 Execution Overhead

Additional API calls, processing time, and computational resources required by the recovery mechanism.

Metric definitions, measurement procedures, and statistical methods will be refined before comparative experiments.

## 8. Reproducibility

The research will maintain:

* Version-controlled source code.
* Documented experiment configurations.
* Automated tests.
* Explicit software dependencies.
* Repeatable execution commands.
* Recorded experiment results.
* Documented assumptions and limitations.

### Installation

```bash
python -m pip install -e ".[dev]"
```

### Execute Baseline

```bash
python experiments/baselines/naive_retry.py
```

### Run Automated Tests

```bash
python -m pytest -v
```

Future benchmark releases will record environment versions, random seeds where applicable, repeated trial results, and statistical uncertainty.

## 9. Threats to Validity

The initial baseline has several limitations:

1. The experiment uses an in-memory simulation rather than a production utility system.
2. No actual API timeout
