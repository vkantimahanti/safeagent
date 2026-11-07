from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ServiceTicket:
    ticket_id: str
    customer_id: str
    issue: str
    status: str = "OPEN"


class IdempotentUtilityService:
    """
    Simulated utility service with idempotency protection.

    Repeated requests with the same operation ID return
    the original ticket.

    This implementation is in-memory and single-process.
    """

    def __init__(self) -> None:
        self._tickets: Dict[str, ServiceTicket] = {}
        self._operations: Dict[str, tuple[str, str, str]] = {}
        self._next_ticket_id = 1001

    def create_ticket(
        self,
        customer_id: str,
        issue: str,
        operation_id: str,
    ) -> ServiceTicket:

        if not operation_id:
            raise ValueError("operation_id cannot be empty")

        # Check whether this logical operation was executed.
        if operation_id in self._operations:
            saved_customer, saved_issue, ticket_id = (
                self._operations[operation_id]
            )

            # Reject accidental reuse for a different request.
            if (saved_customer, saved_issue) != (customer_id, issue):
                raise ValueError(
                    "operation_id was already used for a different request"
                )

            return self._tickets[ticket_id]

        # Create a ticket for a new logical operation.
        ticket_id = f"T-{self._next_ticket_id}"
        self._next_ticket_id += 1

        ticket = ServiceTicket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            issue=issue,
        )

        self._tickets[ticket_id] = ticket

        # Associate the operation with its ticket.
        self._operations[operation_id] = (
            customer_id,
            issue,
            ticket_id,
        )

        return ticket

    def list_tickets(self) -> List[ServiceTicket]:
        return list(self._tickets.values())