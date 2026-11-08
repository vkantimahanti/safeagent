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

**Status:** Completed — sequential baseline

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


## EXP-003A: Lost Acknowledgment Simulation

**Status:** Completed — Initial Sequential Evaluation

### Objective

Evaluate how naive and idempotency-aware retry strategies behave when a business operation completes successfully but its acknowledgment is lost.

### Experimental Setup

A controlled failure injector executes a service-ticket creation operation and then raises a simulated `TimeoutError` before returning the result to the caller.

Two recovery strategies were evaluated:

1. Naive retry without an operation identifier.
2. Idempotency-aware retry using a stable operation identifier.

### Observed Results

| Metric                      | Naive Retry | Idempotent Retry |
| --------------------------- | ----------- | ---------------- |
| Intended logical operations | 1           | 1                |
| Execution attempts          | 2           | 2                |
| Lost acknowledgments        | 1           | 1                |
| Tickets created             | 2           | 1                |
| Duplicate tickets           | 1           | 0                |

### Automated Test Results

* Total tests: 8
* Passed: 8
* Failed: 0
* Execution time: 0.09 seconds

### Findings

The simulated acknowledgment loss caused the caller to observe a timeout even though the initial ticket creation succeeded.

Naive retry created a duplicate ticket.

Idempotency-aware retry returned the original ticket without creating an additional record.

### Limitations

* Deterministic, single-process simulation.
* No real HTTP communication.
* No concurrent requests.
* No persistent storage.
* No actual network timeout.
* No statistical performance evaluation.

### Conclusion

The experiment demonstrates that idempotency-aware retry prevents duplicate ticket creation following simulated acknowledgment loss in the implemented sequential environment.

These results support the use of idempotency controls as a baseline recovery mechanism.

Further evaluation is required under additional failure scenarios and execution environments.

---

## EXP-003B: Verification-Based Recovery

**Status:** Completed — deterministic decision tests

### Question and setup

Can the recovery controller avoid an unnecessary retry when the original business operation succeeded but its acknowledgment was lost?

Implemented `VerificationRecoveryController` and `ServiceStateVerifier`. The verifier queries `get_ticket_by_operation(operation_id)`; the controller distinguishes `SUCCESS`, `NOT_EXECUTED`, and `UNKNOWN`.

### Observations

| Input/evidence | Observed decision |
| --- | --- |
| Confirmed success | `STOP` |
| Authoritatively confirmed non-execution | `RETRY` |
| Unknown outcome | `ESCALATE` |
| Verification error or invalid status | `ESCALATE` |
| Ticket found after simulated lost acknowledgment | `SUCCESS` → `STOP` |

An absent operation lookup result was treated as `UNKNOWN`, not proof of non-execution. This distinction prevents a potentially unsafe retry when the registry is incomplete.

### Evidence and limitations

`tests/test_verification_recovery.py` and `tests/test_service_state_verification.py` passed in the reported suite. The controller emits decisions; it does not enforce external authorization. No comparative performance or statistical safety benefit was measured.

## EXP-003C: Thread-Level Concurrency

**Status:** Completed

### Question and setup

Does a sequential idempotency check remain correct when two threads race on the same operation ID?

The unsafe implementation used a barrier to make both threads pass the operation-absence check before creating a ticket. A second implementation protected the complete check-and-create section with a shared lock.

### Observed results

| Metric | Unsafe | Lock-protected |
| --- | ---: | ---: |
| Threads | 2 | 2 |
| Tickets | 2 | 1 |
| Duplicate tickets | 1 | 0 |

The tests `test_concurrent_requests_without_lock_create_duplicates` and `test_concurrent_requests_with_lock_prevent_duplicates` passed.

### Interpretation

A check-then-act race can defeat otherwise correct sequential idempotency logic. Shared locking resolved the tested thread-level race, but does not protect multiple processes or hosts.

### Evidence

`experiments/recovery/concurrent_idempotency.py`; `tests/test_concurrent_idempotency.py`.

## EXP-004A: SQLite Database Initialization

**Status:** Completed

### Implementation

Added `src/safeagent/services/database.py` and `initialize_database(db_path)` to create a SQLite file with `tickets` and `operations` tables. `operations.operation_id` is unique by primary key and references the ticket. The development environment reported SQLite 3.45.3.

### Observation

Database initialization and subsequent database-backed service tests succeeded. The schema provided a persistent operation-to-ticket mapping used by the later experiments.

### Limitations

The schema is local SQLite; no schema migration or alternative database engine has been evaluated.

## EXP-004B: Transactional Persistent Idempotency

**Status:** Completed

### Question and implementation

Can ticket creation and operation registration commit atomically so a retry does not create a second ticket?

`PersistentUtilityService` uses `BEGIN IMMEDIATE`, operation-ID lookup, payload matching, ticket insertion, operation registration, and commit in a single SQLite transaction. Conflicting reuse is rejected.

### Observed results

- First request created a ticket (observed `T-1` in the persistent experiment).
- An identical retry returned the original ticket.
- A newly initialized service object using the same database recovered the committed operation.
- Conflicting payload and empty operation ID were rejected.
- An injected SQLite trigger failure during operation registration rolled back ticket creation, preventing a partial record.

### Debugging record: Windows SQLite file handle

**Symptom:** Temporary database cleanup raised `PermissionError: [WinError 32]` on Windows.

**Cause identified:** `with sqlite3.connect(...) as conn` manages transaction commit/rollback but does not close the underlying connection.

**Correction:** Explicitly close SQLite connections with `contextlib.closing(...)` in database initialization and persistent-service methods.

**Outcome:** The persistent-service test suite subsequently passed.

### Evidence

`src/safeagent/services/database.py`; `src/safeagent/services/persistent_utility_service.py`; `tests/test_persistent_utility_service.py`.

### Limitations

Reinitializing a service object does not simulate forced process termination. No high-contention latency benchmark was conducted.

## EXP-004C: Two-Process Idempotency

**Status:** Completed

### Setup

Used `ProcessPoolExecutor` to submit the same operation ID from two independent Python processes against one shared SQLite file. Transaction coordination used `BEGIN IMMEDIATE`.

### Observed results

Both processes returned `T-1`, while the database contained one committed ticket. The multiprocess pytest test passed.

### Interpretation and limitations

The result supports idempotent behavior in this two-process, local SQLite scenario. It does not establish behavior under many workers, arbitrary scheduling, a distributed database, or process crashes.

**Evidence:** `tests/test_multiprocess_idempotency.py`.

## EXP-004D: Persistent Verification After Acknowledgment Loss

**Status:** Completed

### Setup

1. Execute and commit a ticket creation.
2. Simulate acknowledgment loss after the business side effect.
3. Reinitialize `PersistentUtilityService` using the same SQLite file.
4. Verify the original operation ID.
5. Apply the recovery controller.

### Observed results

The committed operation was found. Verification returned `SUCCESS`; recovery returned `STOP`. The test found no duplicate ticket.

**Evidence:** `tests/test_persistent_acknowledgment_recovery.py`.

**Limitations:** Simulated Python timeout, not a real dropped HTTP response. Reinitialized object, not an abruptly killed and restarted server.

## EXP-005: Initial FastAPI Integration

**Status:** In progress — HTTP health and root routes tested

### Environment and implementation

- Python 3.12.7; pytest 9.2.0.
- FastAPI 0.162.2; Uvicorn 0.54.0; HTTPX 0.28.1 (reported installed versions).
- `src/safeagent/api/main.py` defines `GET /health` and `GET /`.

### Observed debugging sequence

An initial browser request to `/` returned HTTP 404 because the root route had not yet been defined. `/favicon.ico` also returned 404, which is normal when no favicon route is configured.

The running Uvicorn server returned HTTP 200 for `GET /health`, with `{"status": "healthy", "service": "safeagent"}`. The root route was subsequently added.

Two FastAPI `TestClient` tests passed independently:

- `tests/test_api_health.py::test_health_endpoint`
- `tests/test_api_health.py::test_home_endpoint`

The test run emitted a `StarletteDeprecationWarning` concerning `httpx` and `starlette.testclient`; this did not cause a failure.

### Test-count reconciliation

**Confirmed full suite:** `29 passed in 1.21s`, collecting 29 tests. This full-suite output did **not** list the two API tests.

**Confirmed focused run:** `2 passed, 1 warning in 0.65s` for `tests/test_api_health.py`.

**Not yet evidenced:** A single full-suite execution collecting and passing all 31 tests. Do not record `31 passed` until that output is captured.

### Next steps

1. Confirm full pytest discovery of all API and service tests.
2. Add `POST /tickets` with isolated test database and payload-conflict behavior.
3. Add operation verification endpoint.
4. Test genuine HTTP-boundary failure and recovery scenarios.
5. Preserve exact commands, logs, commit hashes, and failure-injection settings for future public release.

## Research Evidence Register

| Milestone | Recorded evidence | Scope of claim |
| --- | --- | --- |
| EXP-001 | T-1001 then T-1002 | Deterministic duplicate baseline |
| EXP-002 | 5 tests passed, 0.06 s | Sequential in-memory idempotency |
| EXP-003A | 8 tests passed, 0.09 s | Simulated post-execution acknowledgment loss |
| EXP-003B | Verification controller and service-verifier tests passed | Correct decision mappings in tested cases |
| EXP-003C | 2 tickets unsafe; 1 locked | Two-thread controlled race |
| EXP-004A–D | 29-test full suite passed (1.21 s in most recent shared run; earlier 1.35 s) | Persistent service, rollback, two-process coordination, verification |
| EXP-005 initial | 2 focused API tests passed (0.65 s), health HTTP 200 | Basic HTTP route behavior, not ticket API reliability |

**Research integrity and publication readiness.** The recorded work demonstrates incremental engineering and experiment design. It does not yet establish a novel algorithm, production-grade agent safety, statistical superiority, independent replication, peer-reviewed acceptance, or EB-1A eligibility. Future claims must be tied to preserved raw evidence, source revisions, independent validation, and appropriate literature context.



---

# Research Journal Continuation — EXP-005 through EXP-007 (2026-11-08)

> **Historical continuity:** Entries above are retained without deletion. Earlier EXP-005 “in progress” and 29-test statements reflect their original date and are superseded by the verified milestones below. Experiment numbering now reserves EXP-006 for benchmarking and EXP-007 for risk-aware policy.

## EXP-005 — HTTP API and recovery progression

- **005A–C:** Added FastAPI health/root routes, `POST /tickets`, and `GET /operations/{operation_id}`. Request validation, replay behavior, and HTTP 409 conflict behavior were tested. Missing operation returns `UNKNOWN`, not authoritative non-execution.
- **005D:** Controlled test omitted a successful POST acknowledgment; subsequent GET confirmed the ticket. A second test demonstrated safe same-ID replay. **39 full-suite tests passed** at this milestone.
- **005E–F:** Added `SafeAgentHTTPRecoveryClient`; refactored it to reuse `VerificationRecoveryController`. Debugged an initial mistake returning `RecoveryResult` instead of `.decision`. **41 tests passed**.
- **005G:** Introduced an `httpx.AsyncBaseTransport` wrapper that processes POST then raises `ReadTimeout`, emulating acknowledgment loss. **42 tests passed**.
- **005H:** Added asynchronous verification/recovery client; timeout followed by successful verification returned STOP. **43 tests passed**.
- **005I:** Simulated POST acknowledgment loss and subsequent verification GET failure; selected ESCALATE. **44 tests passed**.
- **005J:** Recreated the service object against the same SQLite DB; verified prior operation and STOP. **45 tests passed**.
- **005K:** Used separate cleanly exited Python processes to test persistent operation verification. **46 tests passed**. This was **not** a forced crash.

**Fault model:** In-process HTTPX ASGI transport interception, not external network packet loss. The client can observe timeout after a committed DB side effect. No automatic blind retry is performed for `UNKNOWN`.

## EXP-006 — Benchmarks and concurrency

### EXP-006A — Duplicate rate

100 naive trials yielded a **100%** duplicate rate; 100 in-memory idempotent trials yielded **0%** duplicates. Mean measured operation times were **0.0033 ms** and **0.0027 ms**. These rates are deterministic outcomes of the constructed workload, not field reliability estimates. Result path reported: `results/exp006a/duplicate_rate.csv`.

### EXP-006B — Persistent latency

Across 100 trials per strategy, mean latencies were **0.0124 ms** (naive), **0.0090 ms** (in-memory idempotent), and **7.1360 ms** (SQLite persistent). Median latencies were **0.0111**, **0.0083**, and **6.5817 ms**; maxima were **0.0712**, **0.0316**, and **25.8900 ms**. Persistent storage offers a different durability contract and these timings should not be interpreted as matched overhead.

### EXP-006C — Concurrent workload

For worker counts 1/2/5/10, with 10 trials each, mean wall times were **10.57/16.00/51.37/126.50 ms**. Mean per-worker latencies were **6.52/9.11/24.75/55.44 ms**. The run reported **180 successful requests** and a single returned ticket ID per trial. This workload was not proof of simultaneous entry into SQLite's write transaction.

### EXP-006D — Synchronized SQLite concurrency

Ten threads synchronized before issuing the same logical operation. All returned one unique ticket ID. Independent queries found **1 committed ticket** and **1 operation**. Debugging note: SQLite connections used for final assertions must be explicitly closed with `contextlib.closing` on Windows to avoid `WinError 32` during temporary DB cleanup.

### EXP-006E — Concurrent HTTP acknowledgment loss

Five asynchronous HTTP clients using injected acknowledgment loss shared one operation ID; each verified success and returned STOP. Database checks found one committed ticket and operation. **47 full-suite tests passed**.

### EXP-006F — Mixed HTTP outcomes

Five clients shared an operation ID: two observed HTTP success and three observed simulated timeout, then verified STOP. Database invariant remained one ticket and one operation. **48 full-suite tests passed**.

### EXP-006G — Repeated recovery decisions

Three deterministic scenarios, 100 trials each: A acknowledgment loss/verification SUCCESS→STOP; B acknowledgment loss/verification failure→ESCALATE; C missing operation→ESCALATE. **300/300 expected decisions** were reported. Mean recovery-phase latency: **A 4.1316 ms, B 0.2356 ms, C 2.4436 ms**; median **3.9376/0.2132/2.3289 ms**; P95 **5.8758/0.3510/2.9952 ms**. The very fast B result reflects immediate injected timeout rather than real network waiting. Result file: `results/exp006g/recovery_reliability.csv`.

### EXP-006H — Randomized order and delayed verification

Configured **100 trials/scenario**, random seed **42**, a **50 ms** injected delay before verification failure, and client-workflow timing. An initial run failed because the new delayed transport forwarded a POST without returning the underlying HTTP response, causing `AttributeError: 'NoneType' object has no attribute 'aclose'` in the outer acknowledgment-loss transport. Added an explicit `return await self.wrapped_transport.handle_async_request(request)` and a forwarding regression test. **49 full-suite tests passed** after the fix. User subsequently reported the benchmark completed successfully. **Numerical benchmark results were not provided/reviewed** and must not be inferred.

## EXP-007 — Risk-aware recovery

### EXP-007A — Policy implementation and tests

Implemented `RiskAwareRecoveryController` with operation risk LOW/MEDIUM/HIGH. For verified SUCCESS, STOP; for UNKNOWN, ESCALATE; for authoritative NOT_EXECUTED, LOW/MEDIUM→RETRY, HIGH→ESCALATE pending authorization. **Nine parameterized tests passed; 58 total tests passed**. This validates expected mapping, not safety superiority.

### EXP-007B — Trusted operation registry (pending verification)

Proposed `OperationDefinition` Pydantic model and registry: `READ_CUSTOMER` LOW, `CREATE_TICKET` MEDIUM, `DISCONNECT_POWER` HIGH/authorization required. Five tests were provided, but **no test output has been confirmed**. Do not mark EXP-007B completed or claim 63 tests without execution evidence.

### Planned EXP-007C/D, EXP-008, EXP-009

Integrate LangGraph orchestration and then an LLM-powered agent; inject randomized failures into agent workflows; test persistence/checkpoints and recovery across interruptions; compare against explicitly defined baseline strategies. Stop after EXP-009 for research-readiness assessment. The agent must not independently downgrade risk classification; the trusted policy registry controls that input.

## Latest verified status and open evidence gaps

| Item | Last confirmed status |
| --- | --- |
| Full automated test suite | **58 passed** after EXP-007A |
| EXP-007B tests | Not yet reported |
| EXP-006H benchmark | Completed by user report; metrics not reviewed |
| Real network-failure injection | Not evaluated |
| LLM / LangGraph agent | Not implemented or verified |
| Crash consistency | Not evaluated under forced termination |
| Comparative risk-aware benefit | Not yet established |

**Evidence retention action:** Before Git push, preserve raw benchmark CSVs, commit hash, relevant terminal outputs, dependency snapshot, and any failed run logs. A passing test is evidence only for its defined assertions and fault model.
