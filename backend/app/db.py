import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "afip.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute(query: str, args: tuple = ()):
    """Execute a query that modifies the database (INSERT, UPDATE, DELETE)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        return cursor.lastrowid

def fetch_all(query: str, args: tuple = ()):
    """Fetch multiple rows from the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        return [dict(row) for row in cursor.fetchall()]

def fetch_one(query: str, args: tuple = ()):
    """Fetch a single row from the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        row = cursor.fetchone()
        return dict(row) if row else None

def init_db():
    """Initializes the database schema if it doesn't exist."""
    # We can import seed.py logic here later if needed to run schema from app
    pass
