from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import multiprocessing

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


def create_ticket_worker(db_path, start_event):
    """
    Each worker creates its own service instance and
    database connection.
    """
    service = PersistentUtilityService(db_path)

    # Wait until the parent allows workers to start.
    if not start_event.wait(timeout=15):
        raise TimeoutError("Worker start signal timed out")

    ticket = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-101",
    )

    return ticket.ticket_id


def run_experiment():
    with TemporaryDirectory() as directory:
        db_path = str(Path(directory) / "safeagent.db")

        # Initialize database before starting workers.
        service = PersistentUtilityService(db_path)

        # Windows requires spawn-compatible multiprocessing.
        context = multiprocessing.get_context("spawn")

        with context.Manager() as manager:
            start_event = manager.Event()

            with ProcessPoolExecutor(
                max_workers=2,
                mp_context=context,
            ) as executor:

                futures = [
                    executor.submit(
                        create_ticket_worker,
                        db_path,
                        start_event,
                    )
                    for _ in range(2)
                ]

                # Release both workers.
                start_event.set()

                results = [
                    future.result(timeout=30)
                    for future in futures
                ]

        tickets = service.list_tickets()

        print("\n--- Multiprocess Idempotency Experiment ---")
        print("Returned ticket IDs:", results)
        print("Stored ticket IDs:", [t.ticket_id for t in tickets])
        print("Total tickets:", len(tickets))

        assert results == ["T-1", "T-1"]
        assert len(tickets) == 1


if __name__ == "__main__":
    run_experiment()