# SafeAgent — Architecture (Pre-LangGraph Checkpoint)

## Implemented layers

```text
Caller / simulated HTTP client
    |
    v
HTTPX transport (optional injected acknowledgment loss)
    |
    v
FastAPI: POST /tickets; GET /operations/{operation_id}
    |
    v
PersistentUtilityService
    |
    +-- SQLite transaction: tickets + operations
    |
    v
Verification endpoint / ServiceStateVerifier
    |
    v
Recovery controller: STOP, RETRY, ESCALATE
    |
    +-- EXP-007A risk-aware policy (proposed risk classes)
```

## Responsibilities

- **API:** Validate request schema and expose ticket creation and operation lookup.
- **Persistence:** Atomically bind a stable operation ID to its business side effect.
- **Verification:** Return committed evidence when available; missing evidence is `UNKNOWN`.
- **Recovery policy:** Convert evidence into a bounded decision; no blind retry on unknown outcomes.
- **Risk-aware policy:** Require authorization for high-risk retry even after confirmed non-execution.
- **Fault injection:** Simulate acknowledgment and verification failures for controlled experiments.

## Planned LangGraph architecture (not yet implemented)

```text
LLM proposes operation --> Trusted operation registry / authorization gate
                                   |
                                   v
                           LangGraph execution node
                                   |
                              tool / FastAPI
                                   |
                          success or uncertain outcome
                                   |
                            verification node
                                   |
                          risk-aware policy node
                                   |
                          STOP / RETRY / ESCALATE
                                   |
                          checkpoint / audit record
```

The LLM must not be the authority on operation risk, authorization, or whether a committed side effect can be retried. LangGraph's checkpointing is an existing framework capability, not a SafeAgent invention. Any retry after `NOT_EXECUTED` requires authoritative evidence and appropriate authorization.

## Boundaries and caveats

Current benchmarks use local SQLite and in-process HTTPX ASGI transports. They do not prove distributed exactly-once execution, crash-safe external effects, or end-to-end LLM-agent reliability.
