import sqlite3
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class PriorAuthorizationRecord:
    authorization_id: int
    member_id: str
    procedure_code: str
    operation_id: str
    status: str


class PersistentPriorAuthService:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_database()

    @contextmanager
    def _connect(self):
        """
        Manage SQLite connections safely.

        - Commit successful transactions.
        - Roll back failed transactions.
        - Always close the connection.
        """
        conn = sqlite3.connect(self.db_path, timeout=10)

        try:
            yield conn
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    def _initialize_database(self):
        """
        Create the prior authorization table if it does not exist.
        """
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prior_authorizations (
                    authorization_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT NOT NULL,
                    procedure_code TEXT NOT NULL,
                    operation_id TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL
                )
            """)

    def submit_prior_auth(
        self,
        member_id: str,
        procedure_code: str,
        operation_id: str,
    ) -> PriorAuthorizationRecord:
        """
        Submit a prior authorization request.

        If the operation_id already exists:
        - Return the existing authorization when request data matches.
        - Raise an error when request data differs.

        This provides persistent idempotency.
        """

        with self._connect() as conn:

            # Acquire a write lock before checking for an existing operation.
            conn.execute("BEGIN IMMEDIATE")

            existing = conn.execute(
                """
                SELECT
                    authorization_id,
                    member_id,
                    procedure_code,
                    operation_id,
                    status
                FROM prior_authorizations
                WHERE operation_id = ?
                """,
                (operation_id,),
            ).fetchone()

            if existing:
                record = PriorAuthorizationRecord(*existing)

                if (
                    record.member_id != member_id
                    or record.procedure_code != procedure_code
                ):
                    raise ValueError(
                        "Operation ID reused with different request data"
                    )

                return record

            # Create a new authorization only if the operation is new.
            cursor = conn.execute(
                """
                INSERT INTO prior_authorizations (
                    member_id,
                    procedure_code,
                    operation_id,
                    status
                )
                VALUES (?, ?, ?, 'SUBMITTED')
                """,
                (
                    member_id,
                    procedure_code,
                    operation_id,
                ),
            )

            return PriorAuthorizationRecord(
                authorization_id=cursor.lastrowid,
                member_id=member_id,
                procedure_code=procedure_code,
                operation_id=operation_id,
                status="SUBMITTED",
            )

    def get_by_operation(
        self,
        operation_id: str,
    ) -> PriorAuthorizationRecord | None:
        """
        Retrieve an existing authorization using its operation ID.
        """

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    authorization_id,
                    member_id,
                    procedure_code,
                    operation_id,
                    status
                FROM prior_authorizations
                WHERE operation_id = ?
                """,
                (operation_id,),
            ).fetchone()

        return PriorAuthorizationRecord(*row) if row else None

    def count_authorizations(self) -> int:
        """
        Return the total number of authorization records.
        """

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*)
                FROM prior_authorizations
                """
            ).fetchone()

        return row[0]