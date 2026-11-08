import threading
from concurrent.futures import ThreadPoolExecutor


class UnsafeTicketService:
    """
    Deliberately unsafe implementation for demonstrating
    a check-then-act race condition.
    """

    def __init__(self):
        self.operations = {}
        self.tickets = []
        self.barrier = threading.Barrier(2)
        self.lock = threading.Lock()

    def create_ticket(self, operation_id):
        # Both threads check before either creates a ticket.
        if operation_id in self.operations:
            return self.operations[operation_id]

        # Force both threads to reach this point.
        self.barrier.wait(timeout=5)

        # Protect only ticket-number allocation, not idempotency.
        with self.lock:
            ticket_id = f"T-{1001 + len(self.tickets)}"
            self.tickets.append(ticket_id)

        self.operations[operation_id] = ticket_id

        return ticket_id


class SafeTicketService:
    """
    Uses a shared lock to protect the entire
    check-and-create operation.
    """

    def __init__(self):
        self.operations = {}
        self.tickets = []
        self.lock = threading.Lock()

    def create_ticket(self, operation_id):
        with self.lock:
            if operation_id in self.operations:
                return self.operations[operation_id]

            ticket_id = f"T-{1001 + len(self.tickets)}"

            self.tickets.append(ticket_id)
            self.operations[operation_id] = ticket_id

            return ticket_id


def run_experiment(service):
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(service.create_ticket, "OP-101")
            for _ in range(2)
        ]

        results = [future.result() for future in futures]

    return results, service.tickets


if __name__ == "__main__":
    print("\n--- Concurrent Execution Without Locking ---")

    unsafe_service = UnsafeTicketService()
    results, tickets = run_experiment(unsafe_service)

    print(f"Returned tickets: {results}")
    print(f"Created tickets: {tickets}")
    print(f"Total tickets: {len(tickets)}")

    print("\n--- Concurrent Execution With Locking ---")

    safe_service = SafeTicketService()
    results, tickets = run_experiment(safe_service)

    print(f"Returned tickets: {results}")
    print(f"Created tickets: {tickets}")
    print(f"Total tickets: {len(tickets)}")