import sqlite3

import pytest

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


@pytest.fixture
def service(tmp_path):
    return PersistentUtilityService(str(tmp_path / "test.db"))


def test_first_request_creates_ticket(service):
    ticket = service.create_ticket(
        "CUST-101", "Power outage", "OP-101"
    )

    assert ticket.ticket_id == "T-1"
    assert len(service.list_tickets()) == 1


def test_retry_returns_original_ticket(service):
    first = service.create_ticket(
        "CUST-101", "Power outage", "OP-101"
    )

    retry = service.create_ticket(
        "CUST-101", "Power outage", "OP-101"
    )

    assert first.ticket_id == retry.ticket_id
    assert len(service.list_tickets()) == 1


def test_operation_survives_service_reinitialization(tmp_path):
    db_path = str(tmp_path / "persistent.db")

    service1 = PersistentUtilityService(db_path)

    first = service1.create_ticket(
        "CUST-101", "Power outage", "OP-101"
    )

    service2 = PersistentUtilityService(db_path)

    retry = service2.create_ticket(
        "CUST-101", "Power outage", "OP-101"
    )

    assert first.ticket_id == retry.ticket_id
    assert len(service2.list_tickets()) == 1


def test_conflicting_payload_is_rejected(service):
    service.create_ticket(
        "CUST-101", "Power outage", "OP-101"
    )

    with pytest.raises(ValueError):
        service.create_ticket(
            "CUST-999", "Different issue", "OP-101"
        )

    assert len(service.list_tickets()) == 1


def test_empty_operation_id_is_rejected(service):
    with pytest.raises(ValueError):
        service.create_ticket(
            "CUST-101", "Power outage", ""
        )

    assert len(service.list_tickets()) == 0


def test_transaction_rollback_prevents_partial_ticket(service):
    """
    Force operation registration to fail after ticket insertion.
    Both changes must roll back.
    """

    with sqlite3.connect(service.db_path) as conn:
        conn.execute("""
            CREATE TRIGGER reject_operation
            BEFORE INSERT ON operations
            BEGIN
                SELECT RAISE(ABORT, 'Simulated operation failure');
            END;
        """)

    with pytest.raises(sqlite3.IntegrityError):
        service.create_ticket(
            "CUST-101", "Power outage", "OP-101"
        )

    assert len(service.list_tickets()) == 0