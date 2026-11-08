# SafeAgent — Roadmap Through EXP-009

**Agreed development stopping point:** Complete EXP-009 and conduct a research-readiness review before deciding whether to expand scope.

## Completed and verified

- EXP-001–006F: foundational execution, persistence, API, concurrency, and HTTP fault-injection experiments.
- EXP-006G: 300 deterministic recovery-policy decisions, all matching expected outcomes.
- EXP-006H: randomized delayed-failure benchmark executed; numeric output pending review.
- EXP-007A: nine risk-aware policy tests passed; full suite 58 passed.

## Next steps

| ID | Deliverable | Acceptance evidence |
|---|---|---|
| EXP-007B | Trusted Pydantic operation registry | Five registry tests and full suite pass; risk labels not controlled by LLM |
| EXP-007C | First LangGraph workflow | Graph executes ticket tool, verifies ambiguous result, selects recovery action |
| EXP-007D | LLM tool-selection agent | LLM proposes actions; registry enforces risk and authorization; deterministic test harness |
| EXP-008A | Randomized faults | Seeded scenarios and recorded fault schedule |
| EXP-008B | Agent workflow recovery | Checkpoint/resumption tests; no duplicate external side effect in tested cases |
| EXP-008C | Baseline comparison | Same scenarios for naive retry, verification-only, and risk-aware policies |
| EXP-009A | Process interruption | Controlled termination at documented execution points |
| EXP-009B | Restart/reconciliation | Restore graph state and reconcile external operation records |
| EXP-009C | Research-readiness review | Reproducible metrics, uncertainty, limitations, and novelty assessment |

## Evidence required for research claims

- Ground-truth business-operation state measured independently of agent decisions.
- Explicit failure-model boundaries and safety assumptions.
- Comparable baselines and matched workload conditions.
- Repeated runs, latency percentiles, confidence intervals where appropriate.
- Clear distinction between simulated timeouts and real network failures.
- Explicit separation of established mechanisms from any demonstrated novel contribution.

No publication or EB-1A outcome is guaranteed by completing the roadmap.
