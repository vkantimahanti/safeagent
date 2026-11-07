from safeagent.services.utility_service import UtilityService


def test_repeated_requests_create_duplicate_tickets():
    service = UtilityService()

    first = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
    )

    second = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
    )

    assert first.ticket_id != second.ticket_id
    assert len(service.list_tickets()) == 2