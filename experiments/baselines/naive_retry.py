from safeagent.services.utility_service import UtilityService


def run_experiment() -> None:
    service = UtilityService()

    first_response = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
    )

    retry_response = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
    )

    tickets = service.list_tickets()

    print(f"First ticket: {first_response.ticket_id}")
    print(f"Retry ticket: {retry_response.ticket_id}")
    print(f"Total tickets: {len(tickets)}")
    print(f"Duplicate tickets: {len(tickets) - 1}")


if __name__ == "__main__":
    run_experiment()