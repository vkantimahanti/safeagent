from safeagent.services.idempotent_utility_service import (
    IdempotentUtilityService,
)


def run_experiment() -> None:

    service = IdempotentUtilityService()

    first = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    retry = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    new_request = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-102",
    )

    tickets = service.list_tickets()

    print(f"First ticket: {first.ticket_id}")
    print(f"Retry ticket: {retry.ticket_id}")
    print(f"New request ticket: {new_request.ticket_id}")
    print(f"Total tickets: {len(tickets)}")
    print(f"Retry returned original: {first.ticket_id == retry.ticket_id}")


if __name__ == "__main__":
    run_experiment()