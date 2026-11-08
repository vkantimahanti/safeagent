import sqlite3
from pathlib import Path
from contextlib import closing

def initialize_database(db_path: str):
    """Initialize the persistent SafeAgent database."""

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                issue TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'OPEN'
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                operation_id TEXT PRIMARY KEY,
                ticket_id INTEGER NOT NULL UNIQUE,
                customer_id TEXT NOT NULL,
                issue TEXT NOT NULL,
                FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
            )
        """)

        conn.commit()