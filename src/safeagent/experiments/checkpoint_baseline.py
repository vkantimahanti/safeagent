from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


def run_checkpoint_only_baseline(db_path: str) -> dict:
    """
    Simulates a checkpoint that was not updated after
    the external operation committed.

    Baseline policy:
    Retry with a new operation ID because the checkpoint
    does not record successful completion.
    """

    service = PersistentUtilityService(db_path)

    # First execution succeeds.
    service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id="checkpoint-attempt-001",
    )

    # Simulated crash before checkpoint update.
    checkpoint_tool_completed = False

    if not checkpoint_tool_completed:
        service.create_ticket(
            customer_id="CUST-001",
            issue="Power outage",
            operation_id="checkpoint-attempt-002",
        )

    return {
        "ticket_count": len(service.list_tickets()),
        "retry_attempted": True,
        "checkpoint_tool_completed": checkpoint_tool_completed,
    }


def run_checkpoint_with_stable_id(db_path: str) -> dict:
    """
    Simulates checkpoint recovery using a stable operation ID.

    The external operation commits, but the checkpoint
    does not record completion.
    """

    service = PersistentUtilityService(db_path)

    operation_id = "checkpoint-stable-001"

    # First execution commits successfully.
    service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id=operation_id,
    )

    # Checkpoint remains incomplete.
    checkpoint_tool_completed = False

    retry_attempted = False

    if not checkpoint_tool_completed:
        retry_attempted = True

        # Retry with the SAME operation ID.
        service.create_ticket(
            customer_id="CUST-001",
            issue="Power outage",
            operation_id=operation_id,
        )

    return {
        "ticket_count": len(service.list_tickets()),
        "retry_attempted": retry_attempted,
        "checkpoint_tool_completed": checkpoint_tool_completed,
    }