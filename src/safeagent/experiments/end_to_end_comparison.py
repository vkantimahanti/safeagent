from safeagent.services.utility_service import UtilityService
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)
from safeagent.agents.persistent_recovery_workflow import (
    build_persistent_recovery_workflow,
)

def run_naive_post_commit_failure():
    """
    Simulate an acknowledgment lost after a successful commit.

    The caller retries because it does not know
    whether the first operation succeeded.
    """

    service = UtilityService()

    customer_id = "MEMBER-001"
    issue = "Prior authorization request"

    # First execution succeeds.
    service.create_ticket(
        customer_id=customer_id,
        issue=issue,
    )

    # Simulate lost acknowledgment.
    # The caller does not receive the success response.

    # Naive recovery: retry the operation.
    service.create_ticket(
        customer_id=customer_id,
        issue=issue,
    )

    return {
        "approach": "naive",
        "fault": "POST_COMMIT_ACK_LOSS",
        "ticket_count": len(service.list_tickets()),
        "recovery_retries": 1,
        "duplicate_count": max(
            0,
            len(service.list_tickets()) - 1,
        ),
    }


def run_idempotent_post_commit_failure(db_path: str):
    """
    Simulate a lost acknowledgment after a successful SQLite commit.

    Recovery retries using the original operation ID.
    """

    service = PersistentUtilityService(db_path)

    customer_id = "MEMBER-001"
    issue = "Prior authorization request"
    operation_id = "exp010-idempotent-001"

    # Initial execution commits successfully.
    service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=operation_id,
    )

    # Simulate lost acknowledgment by ignoring the response.

    # Recovery retries with the SAME operation ID.
    service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=operation_id,
    )

    tickets = service.list_tickets()

    return {
        "approach": "idempotent",
        "fault": "POST_COMMIT_ACK_LOSS",
        "ticket_count": len(tickets),
        "recovery_retries": 1,
        "duplicate_count": max(0, len(tickets) - 1),
    }


def run_safeagent_post_commit_failure(db_path: str):
    """
    Simulate acknowledgment loss after a successful commit.

    SafeAgent verifies the persisted outcome before
    making a recovery decision.
    """

    service = PersistentUtilityService(db_path)

    customer_id = "MEMBER-001"
    issue = "Prior authorization request"
    operation_id = "exp010-safeagent-001"

    # Step 1: Initial execution succeeds.
    service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=operation_id,
    )

    # Step 2: Simulate lost acknowledgment.
    # The caller does not receive the success response.

    # Step 3: Invoke SafeAgent's recovery-only workflow.
    workflow = build_persistent_recovery_workflow()

    result = workflow.invoke({
        "operation_type": "CREATE_TICKET",
        "operation_id": operation_id,
        "customer_id": customer_id,
        "issue": issue,
        "db_path": db_path,
    })

    # Step 4: Inspect actual persisted tickets.
    tickets = service.list_tickets()

    return {
        "approach": "safeagent",
        "fault": "POST_COMMIT_ACK_LOSS",
        "ticket_count": len(tickets),
        "recovery_retries": 0,
        "duplicate_count": max(0, len(tickets) - 1),
        "verification_status": result["verification_status"],
        "recovery_decision": result["recovery_decision"],
    }


def run_checkpoint_post_commit_failure(db_path: str):
    """
    Simulate a stale checkpoint after a successful external commit.

    Recovery retries using the same stable operation ID.
    """

    service = PersistentUtilityService(db_path)

    customer_id = "MEMBER-001"
    issue = "Prior authorization request"
    operation_id = "exp010-checkpoint-001"

    # Initial execution commits successfully.
    service.create_ticket(
        customer_id=customer_id,
        issue=issue,
        operation_id=operation_id,
    )

    # Simulate a checkpoint that still indicates incomplete execution.
    checkpoint = {
        "operation_id": operation_id,
        "execution_complete": False,
    }

    recovery_retries = 0

    if not checkpoint["execution_complete"]:
        recovery_retries += 1

        service.create_ticket(
            customer_id=customer_id,
            issue=issue,
            operation_id=checkpoint["operation_id"],
        )

    tickets = service.list_tickets()

    return {
        "approach": "checkpoint_stable",
        "fault": "POST_COMMIT_ACK_LOSS",
        "ticket_count": len(tickets),
        "recovery_retries": recovery_retries,
        "duplicate_count": max(0, len(tickets) - 1),
    }



def run_safeagent_missing_operation(db_path: str):
    """
    Simulate an operation with no persisted execution record.

    An absent record is treated as UNKNOWN because
    absence alone does not prove non-execution.
    """

    service = PersistentUtilityService(db_path)

    operation_id = "exp010-missing-operation-001"

    # Deliberately do not execute create_ticket().

    workflow = build_persistent_recovery_workflow()

    result = workflow.invoke({
        "operation_type": "CREATE_TICKET",
        "operation_id": operation_id,
        "customer_id": "MEMBER-001",
        "issue": "Prior authorization request",
        "db_path": db_path,
    })

    return {
        "approach": "safeagent",
        "fault": "MISSING_OPERATION_RECORD",
        "ticket_count": len(service.list_tickets()),
        "verification_status": result["verification_status"],
        "recovery_decision": result["recovery_decision"],
    }