from unittest.mock import patch

from safeagent.agents.persistent_recovery_workflow import (
    build_persistent_recovery_workflow,
)
from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


def test_verification_outage_escalates_without_retry(tmp_path):
    db_path = str(tmp_path / "healthcare_outage.db")

    operation_id = "healthcare-auth-001"

    # Simulated healthcare administrative request.
    service = PersistentUtilityService(db_path)

    service.create_ticket(
        customer_id="MEMBER-001",
        issue="Prior authorization request",
        operation_id=operation_id,
    )

    # Simulate verification database failure.
    with patch.object(
        PersistentUtilityService,
        "get_ticket_by_operation",
        side_effect=ConnectionError("Verification database unavailable"),
    ):
        workflow = build_persistent_recovery_workflow()

        result = workflow.invoke({
            "operation_type": "CREATE_TICKET",
            "operation_id": operation_id,
            "customer_id": "MEMBER-001",
            "issue": "Prior authorization request",
            "db_path": db_path,
        })

    # SafeAgent must not assume success or failure.
    assert result["verification_status"] == "UNKNOWN"

    # Unknown outcome requires escalation.
    assert result["recovery_decision"] == "ESCALATE"

    # No additional ticket should be created.
    assert len(service.list_tickets()) == 1