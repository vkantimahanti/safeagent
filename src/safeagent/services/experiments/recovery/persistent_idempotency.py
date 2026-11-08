from pathlib import Path
from tempfile import TemporaryDirectory

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


with TemporaryDirectory() as directory:
    db_path = str(Path(directory) / "safeagent.db")

    print("\n--- First Request ---")

    service = PersistentUtilityService(db_path)

    first = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    print("Created:", first.ticket_id)
    print("Total tickets:", len(service.list_tickets()))

    print("\n--- Retry With Same Operation ID ---")

    retry = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    print("Returned:", retry.ticket_id)
    print("Total tickets:", len(service.list_tickets()))

    print("\n--- Reinitialize Service ---")

    restarted_service = PersistentUtilityService(db_path)

    recovered = restarted_service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    print("Recovered:", recovered.ticket_id)
    print("Total tickets:", len(restarted_service.list_tickets()))