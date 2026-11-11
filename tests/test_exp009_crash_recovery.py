from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)

from safeagent.recovery.risk_aware import (
    OperationRisk,
    RiskAwareRecoveryController,
)

from safeagent.recovery.verification import VerificationStatus


def test_recovery_after_ticket_commit(tmp_path):

    db_path = str(tmp_path / "exp009_tickets.db")

    operation_id = "exp009-operation-001"

    # BEFORE CRASH: Execute external operation
    service = PersistentUtilityService(db_path)

    ticket = service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id=operation_id,
    )

    original_ticket_id = ticket.ticket_id

    # SIMULATED CRASH:
    # The workflow loses its in-memory execution result.
    del service
    del ticket

    # AFTER RESTART: Reconnect to persistent database
    recovered_service = PersistentUtilityService(db_path)

    recovered_ticket = recovered_service.get_ticket_by_operation(
        operation_id
    )

    # Verify the committed operation
    assert recovered_ticket is not None
    assert recovered_ticket.ticket_id == original_ticket_id

    verification_status = VerificationStatus.SUCCESS

    controller = RiskAwareRecoveryController()

    recovery = controller.decide(
        risk=OperationRisk.MEDIUM,
        verification_status=verification_status,
    )

    assert recovery.decision.value == "STOP"

    # Verify no duplicate ticket was created
    assert len(recovered_service.list_tickets()) == 1