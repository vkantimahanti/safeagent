import pytest

from safeagent.faults.acknowledgment_loss import (
    AcknowledgmentLossInjector,
)

from safeagent.services.utility_service import UtilityService

from safeagent.services.idempotent_utility_service import (
    IdempotentUtilityService,
)


def test_acknowledgment_loss_occurs_after_ticket_creation():
    service = UtilityService()
    injector = AcknowledgmentLossInjector()

    with pytest.raises(TimeoutError):
        injector.execute(
            service.create_ticket,
            customer_id="CUST-101",
            issue="Power outage",
        )

    assert len(service.list_tickets()) == 1


def test_naive_retry_creates_duplicate_after_timeout():
    service = UtilityService()
    injector = AcknowledgmentLossInjector()

    with pytest.raises(TimeoutError):
        injector.execute(
            service.create_ticket,
            customer_id="CUST-101",
            issue="Power outage",
        )

    retry = injector.execute(
        service.create_ticket,
        customer_id="CUST-101",
        issue="Power outage",
    )

    assert retry.ticket_id == "T-1002"
    assert len(service.list_tickets()) == 2


def test_idempotent_retry_prevents_duplicate_after_timeout():
    service = IdempotentUtilityService()
    injector = AcknowledgmentLossInjector()

    with pytest.raises(TimeoutError):
        injector.execute(
            service.create_ticket,
            customer_id="CUST-101",
            issue="Power outage",
            operation_id="OP-101",
        )

    retry = injector.execute(
        service.create_ticket,
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    assert retry.ticket_id == "T-1001"
    assert len(service.list_tickets()) == 1