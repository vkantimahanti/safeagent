from safeagent.agents.persistent_recovery_workflow import (
    build_persistent_recovery_workflow,
)
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)



def test_committed_operation_recovery(tmp_path):
    db_path = str(tmp_path / "tickets.db")
    operation_id = "exp009-recovery-001"

    service = PersistentUtilityService(db_path)

    original = service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id=operation_id,
    )

    workflow = build_persistent_recovery_workflow()

    result = workflow.invoke({
        "operation_type": "CREATE_TICKET",
        "operation_id": operation_id,
        "db_path": db_path,
    })

    assert result["verification_status"] == "SUCCESS"
    assert result["recovery_decision"] == "STOP"

    tickets = service.list_tickets()

    assert len(tickets) == 1
    assert tickets[0].ticket_id == original.ticket_id


def test_missing_operation_escalates(tmp_path):
    db_path = str(tmp_path / "tickets.db")

    workflow = build_persistent_recovery_workflow()

    result = workflow.invoke({
        "operation_type": "CREATE_TICKET",
        "operation_id": "missing-operation",
        "db_path": db_path,
    })

    assert result["verification_status"] == "UNKNOWN"
    assert result["recovery_decision"] == "ESCALATE"