import sqlite3
from dataclasses import dataclass

from safeagent.services.database import initialize_database
from contextlib import closing


@dataclass(frozen=True)
class ServiceTicket:
    ticket_id: str
    customer_id: str
    issue: str
    status: str


class PersistentUtilityService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        initialize_database(db_path)

    def create_ticket(
        self,
        customer_id: str,
        issue: str,
        operation_id: str,
    ) -> ServiceTicket:

        if not operation_id or not operation_id.strip():
            raise ValueError("operation_id cannot be empty")

        with closing(sqlite3.connect(self.db_path, timeout=10)) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Reserve the database writer slot before checking.
            conn.execute("BEGIN IMMEDIATE")

            try:
                existing = conn.execute(
                    """
                    SELECT t.ticket_id, t.customer_id, t.issue, t.status,
                           o.customer_id, o.issue
                    FROM operations o
                    JOIN tickets t ON t.ticket_id = o.ticket_id
                    WHERE o.operation_id = ?
                    """,
                    (operation_id,),
                ).fetchone()

                if existing:
                    ticket_id, saved_customer, saved_issue, status, op_customer, op_issue = existing

                    if (
                        customer_id != op_customer
                        or issue != op_issue
                    ):
                        raise ValueError(
                            "operation_id already used with different payload"
                        )

                    conn.commit()

                    return ServiceTicket(
                        ticket_id=f"T-{ticket_id}",
                        customer_id=saved_customer,
                        issue=saved_issue,
                        status=status,
                    )

                cursor = conn.execute(
                    """
                    INSERT INTO tickets (customer_id, issue)
                    VALUES (?, ?)
                    """,
                    (customer_id, issue),
                )

                ticket_id = cursor.lastrowid

                conn.execute(
                    """
                    INSERT INTO operations (
                        operation_id, ticket_id, customer_id, issue
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (operation_id, ticket_id, customer_id, issue),
                )

                conn.commit()

                return ServiceTicket(
                    ticket_id=f"T-{ticket_id}",
                    customer_id=customer_id,
                    issue=issue,
                    status="OPEN",
                )

            except Exception:
                conn.rollback()
                raise

    def list_tickets(self):
        with closing(sqlite3.connect(self.db_path)) as conn:
            rows = conn.execute(
                """
                SELECT ticket_id, customer_id, issue, status
                FROM tickets
                ORDER BY ticket_id
                """
            ).fetchall()

        return [
            ServiceTicket(
                ticket_id=f"T-{row[0]}",
                customer_id=row[1],
                issue=row[2],
                status=row[3],
            )
            for row in rows
        ]


    def get_ticket_by_operation(
        self,
        operation_id: str,
    ) -> ServiceTicket | None:
        """
        Look up a committed ticket using its operation ID.

        A missing record does not prove that the operation
        was never executed.
        """

        with closing(sqlite3.connect(self.db_path, timeout=10)) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            row = conn.execute(
                """
                SELECT t.ticket_id, t.customer_id, t.issue, t.status
                FROM operations o
                JOIN tickets t ON t.ticket_id = o.ticket_id
                WHERE o.operation_id = ?
                """,
                (operation_id,),
            ).fetchone()

        if row is None:
            return None

        return ServiceTicket(
            ticket_id=f"T-{row[0]}",
            customer_id=row[1],
            issue=row[2],
            status=row[3],
        )