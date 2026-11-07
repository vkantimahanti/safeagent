# SafeAgent Research Journal

## EXP-001: Naive Retry Baseline

**Status:** Completed

### Research Question

What happens when the same state-changing operation is executed multiple times without idempotency protection?

### Hypothesis

Repeated requests without idempotency protection will create duplicate service tickets.

### Experimental Setup

* Service: UtilityService
* Customer ID: CUST-101
* Issue: Power outage
* Original requests: 1
* Additional retries: 1
* Storage: In-memory Python dictionary

### Observed Results

* First ticket: T-1001
* Retry ticket: T-1002
* Total tickets: 2
* Duplicate tickets: 1

### Conclusion

The naive implementation creates a new ticket for each invocation, even when the caller intends to repeat the same logical operation.

### Limitations

* No network communication
* No persistent storage
* No concurrency testing
* No simulated API timeout
* No AI agent integration

---

## EXP-002: Idempotency-Aware Execution

**Status:** In Progress

### Research Question

Can stable operation identifiers prevent duplicate ticket creation when the same logical request is repeated?

### Hypothesis

Repeated requests using the same operation ID will return the original ticket without creating additional tickets.

### Implementation

An in-memory operation registry maps each operation ID to its associated service ticket.

### Experimental Setup

* Customer ID: CUST-101
* Issue: Power outage
* Operation ID: OP-101
* Repeated calls using OP-101: 2
* Independent operation ID: OP-102

### Results

**Automated Test Execution:** Completed

**Test Summary:**

* Total tests: 5
* Passed: 5
* Failed: 0
* Execution time: 0.06 seconds

**Verified Behaviors:**

1. Repeated calls with the same operation ID return the original ticket.
2. Independent operations create separate tickets.
3. Conflicting reuse of an operation ID is rejected.
4. Empty operation identifiers are rejected.

**Conclusion:**

The idempotency-aware implementation passes the initial sequential correctness tests. These results support the hypothesis that stable operation identifiers can prevent duplicate ticket creation in the current in-memory, single-process implementation.

**Limitations:**

The tests do not yet evaluate concurrent requests, persistence, process failures, or uncertain network outcomes.

