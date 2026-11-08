import sqlite3

from safeagent.services.database import initialize_database


DB_PATH = "data/safeagent.db"

initialize_database(DB_PATH)

with sqlite3.connect(DB_PATH) as conn:
    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name IN ('tickets', 'operations')
        ORDER BY name
    """).fetchall()

print("Database initialized successfully.")
print("Tables:", [table[0] for table in tables])