import pytest

from safeagent.services.idempotent_utility_service import (
    IdempotentUtilityService,
)


def test_retry_returns_original_ticket():
    service = IdempotentUtilityService()

    first = service.create_ticket(
        "CUST-101",
        "Power outage",
        "OP-101",
    )

    retry = service.create_ticket(
        "CUST-101",
        "Power outage",
        "OP-101",
    )

    assert first.ticket_id == retry.ticket_id
    assert len(service.list_tickets()) == 1


def test_new_operation_creates_new_ticket():
    service = IdempotentUtilityService()

    first = service.create_ticket(
        "CUST-101",
        "Power outage",
        "OP-101",
    )

    second = service.create_ticket(
        "CUST-101",
        "Power outage",
        "OP-102",
    )

    assert first.ticket_id != second.ticket_id
    assert len(service.list_tickets()) == 2


def test_conflicting_operation_id_is_rejected():
    service = IdempotentUtilityService()

    service.create_ticket(
        "CUST-101",
        "Power outage",
        "OP-101",
    )

    with pytest.raises(ValueError):
        service.create_ticket(
            "CUST-101",
            "Transformer failure",
            "OP-101",
        )


def test_empty_operation_id_is_rejected():
    service = IdempotentUtilityService()

    with pytest.raises(ValueError):
        service.create_ticket(
            "CUST-101",
            "Power outage",
            "",
        )