from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ServiceTicket:
    ticket_id: str
    customer_id: str
    issue: str
    status: str = "OPEN"


class UtilityService:
    """Simulated utility service-request system.

    Baseline intentionally provides no idempotency protection.
    """

    def __init__(self) -> None:
        self._tickets: Dict[str, ServiceTicket] = {}
        self._next_ticket_id = 1001

    def create_ticket(
        self,
        customer_id: str,
        issue: str,
    ) -> ServiceTicket:

        ticket_id = f"T-{self._next_ticket_id}"
        self._next_ticket_id += 1

        ticket = ServiceTicket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            issue=issue,
        )

        self._tickets[ticket_id] = ticket

        return ticket

    def list_tickets(self) -> List[ServiceTicket]:
        return list(self._tickets.values())