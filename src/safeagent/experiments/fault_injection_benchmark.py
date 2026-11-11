from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)
from safeagent.agents.persistent_recovery_workflow import (
    build_persistent_recovery_workflow,
)


def run_post_commit_failure(db_path: str) -> dict:
    """
    Compare idempotent retry and SafeAgent recovery
    after a real SQLite commit and simulated
    acknowledgment loss.
    """

    customer_id = "CUST-001"
    issue = "Power outage"

    # Baseline: Idempotent retry
    idempotent_service = PersistentUtilityService(
        db_path + ".idempotent.db"
    )

    operation_id = "exp010-idempotent-001"

    idempotent_service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=operation_id,
    )

    # The result is deliberately ignored:
    # acknowledgment loss is simulated here.
    idempotent_service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=operation_id,
    )

    # SafeAgent: Verify before retry
    safeagent_path = db_path + ".safeagent.db"

    safeagent_service = PersistentUtilityService(
        safeagent_path
    )

    safeagent_operation_id = "exp010-safeagent-001"

    safeagent_service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=safeagent_operation_id,
    )

    workflow = build_persistent_recovery_workflow()

    result = workflow.invoke({
        "operation_type": "CREATE_TICKET",
        "operation_id": safeagent_operation_id,
        "customer_id": customer_id,
        "issue": issue,
        "db_path": safeagent_path,
    })

    return {
        "idempotent": {
            "tickets": len(idempotent_service.list_tickets()),
            "retry_attempts": 1,
        },
        "safeagent": {
            "tickets": len(safeagent_service.list_tickets()),
            "retry_attempts": 0,
            "verification": result["verification_status"],
            "decision": result["recovery_decision"],
        },
    }