import time

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)
from safeagent.agents.persistent_recovery_workflow import (
    build_persistent_recovery_workflow,
)


def measure_recovery_latency(db_path: str) -> dict:
    customer_id = "MEMBER-001"
    issue = "Prior authorization request"

    # Idempotency-only baseline
    idempotent_service = PersistentUtilityService(
        db_path + ".idempotent.db"
    )

    operation_id = "latency-idempotent-001"

    idempotent_service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=operation_id,
    )

    start = time.perf_counter()

    idempotent_service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=operation_id,
    )

    idempotent_latency = (
        time.perf_counter() - start
    ) * 1000

    # SafeAgent recovery
    safeagent_path = db_path + ".safeagent.db"

    safeagent_service = PersistentUtilityService(
        safeagent_path
    )

    safeagent_operation_id = "latency-safeagent-001"

    safeagent_service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=safeagent_operation_id,
    )

    workflow = build_persistent_recovery_workflow()

    start = time.perf_counter()

    result = workflow.invoke({
        "operation_type": "CREATE_TICKET",
        "operation_id": safeagent_operation_id,
        "customer_id": customer_id,
        "issue": issue,
        "db_path": safeagent_path,
    })

    safeagent_latency = (
        time.perf_counter() - start
    ) * 1000

    return {
        "idempotent_ms": idempotent_latency,
        "safeagent_ms": safeagent_latency,
        "safeagent_decision": result["recovery_decision"],
    }