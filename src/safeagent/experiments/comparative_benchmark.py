from safeagent.services.utility_service import UtilityService
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)
from safeagent.agents.persistent_recovery_workflow import (
    build_persistent_recovery_workflow,
)

def run_comparative_benchmark(db_path: str):
    """
    Compare naive retry against idempotent retry.

    Scenario:
    The first ticket creation succeeds, but its
    acknowledgment is lost.
    """

    # Baseline A: Naive retry
    naive_service = UtilityService()

    naive_service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
    )

    # Simulate lost acknowledgment by ignoring the result.

    naive_service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
    )

    naive_ticket_count = len(naive_service.list_tickets())

    # Baseline B: Idempotent retry
    idempotent_service = PersistentUtilityService(db_path)

    operation_id = "exp010-operation-001"

    idempotent_service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id=operation_id,
    )

    # Simulate lost acknowledgment by ignoring the result.

    idempotent_service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id=operation_id,
    )

    idempotent_ticket_count = len(
        idempotent_service.list_tickets()
    )

        # Approach D: SafeAgent verification-driven recovery

    safeagent_db_path = db_path + ".safeagent.db"

    safeagent_service = PersistentUtilityService(
        safeagent_db_path
    )

    safeagent_operation_id = "exp010-safeagent-001"

    # The operation commits successfully.
    safeagent_service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id=safeagent_operation_id,
    )

    # Simulate acknowledgment loss.
    # Recovery runs without receiving the original response.

    recovery_workflow = build_persistent_recovery_workflow()

    recovery_result = recovery_workflow.invoke({
        "operation_type": "CREATE_TICKET",
        "operation_id": safeagent_operation_id,
        "customer_id": "CUST-001",
        "issue": "Power outage",
        "db_path": safeagent_db_path,
    })

    safeagent_ticket_count = len(
        safeagent_service.list_tickets()
    )

    
    return {
        "naive": naive_ticket_count,
        "idempotent": idempotent_ticket_count,
        "safeagent": safeagent_ticket_count,
        "safeagent_verification": recovery_result["verification_status"],
        "safeagent_decision": recovery_result["recovery_decision"],
    }