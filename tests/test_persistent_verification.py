from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)

from safeagent.recovery.persistent_verification import (
    verify_persistent_ticket,
)

from safeagent.recovery.verification import VerificationStatus
import pytest

def test_committed_ticket_verifies_success(tmp_path):
    service = PersistentUtilityService(
        str(tmp_path / "tickets.db")
    )

    operation_id = "exp009-verify-001"

    service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id=operation_id,
    )

    result = verify_persistent_ticket(
        service,
        operation_id,
    )

    assert result == VerificationStatus.SUCCESS


def test_missing_ticket_is_unknown(tmp_path):
    service = PersistentUtilityService(
        str(tmp_path / "tickets.db")
    )

    result = verify_persistent_ticket(
        service,
        "nonexistent-operation",
    )

    assert result == VerificationStatus.UNKNOWN




def test_operation_id_rejects_different_payload(tmp_path):
    service = PersistentUtilityService(
        str(tmp_path / "tickets.db")
    )

    operation_id = "exp009-payload-001"

    original = service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id=operation_id,
    )

    with pytest.raises(
        ValueError,
        match="operation_id already used with different payload",
    ):
        service.create_ticket(
            customer_id="CUST-999",
            issue="Power outage",
            operation_id=operation_id,
        )

    tickets = service.list_tickets()

    assert len(tickets) == 1
    assert tickets[0].ticket_id == original.ticket_id



def test_recovery_rejects_mismatched_customer(tmp_path):
    service = PersistentUtilityService(
        str(tmp_path / "tickets.db")
    )

    operation_id = "exp009-mismatch-001"

    service.create_ticket(
        customer_id="CUST-001",
        issue="Power outage",
        operation_id=operation_id,
    )

    result = verify_persistent_ticket(
        service=service,
        operation_id=operation_id,
        expected_customer_id="CUST-999",
        expected_issue="Power outage",
    )

    assert result == VerificationStatus.UNKNOWN