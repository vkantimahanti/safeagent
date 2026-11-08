import sqlite3
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from contextlib import closing

from safeagent.services.persistent_utility_service import (
    PersistentUtilityService,
)


WORKERS = 10


def execute_operation(db_path, barrier):
    service = PersistentUtilityService(db_path)

    # Wait until all workers are ready.
    barrier.wait(timeout=10)

    ticket = service.create_ticket(
        customer_id="CUST-101",
        issue="Power outage",
        operation_id="OP-SYNC-101",
    )

    return ticket.ticket_id


def main():

    with tempfile.TemporaryDirectory() as temp_dir:

        db_path = Path(temp_dir) / "synchronized.db"

        barrier = threading.Barrier(WORKERS)

        with ThreadPoolExecutor(max_workers=WORKERS) as executor:

            futures = [
                executor.submit(
                    execute_operation,
                    db_path,
                    barrier,
                )
                for _ in range(WORKERS)
            ]

            ticket_ids = [
                future.result(timeout=30)
                for future in futures
            ]

        # Independently inspect committed database state.
        with closing(sqlite3.connect(db_path)) as conn:

            ticket_count = conn.execute(
                "SELECT COUNT(*) FROM tickets"
            ).fetchone()[0]

            operation_count = conn.execute(
                "SELECT COUNT(*) FROM operations"
            ).fetchone()[0]


        print(f"Workers: {WORKERS}")
        print(f"Unique returned ticket IDs: {len(set(ticket_ids))}")
        print(f"Committed tickets: {ticket_count}")
        print(f"Committed operations: {operation_count}")

        assert len(set(ticket_ids)) == 1
        assert ticket_count == 1
        assert operation_count == 1

        print("RESULT: PASS — No duplicate committed operation")


if __name__ == "__main__":
    main()