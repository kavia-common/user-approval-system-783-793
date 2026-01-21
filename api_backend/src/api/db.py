from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional

from .config import get_settings


def _row_factory(cursor: sqlite3.Cursor, row: tuple):
    """Convert sqlite rows to dicts keyed by column name."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# PUBLIC_INTERFACE
def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection configured with foreign keys and dict rows."""
    settings = get_settings()
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = _row_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def db_cursor() -> Iterator[sqlite3.Cursor]:
    """Context manager that yields a cursor and commits/rolls back as needed."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# PUBLIC_INTERFACE
def query_one(sql: str, params: Optional[tuple] = None) -> Optional[dict]:
    """Execute a SELECT query and return a single row as dict or None."""
    with db_cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()


# PUBLIC_INTERFACE
def query_all(sql: str, params: Optional[tuple] = None) -> list[dict]:
    """Execute a SELECT query and return all rows as list of dicts."""
    with db_cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()


# PUBLIC_INTERFACE
def execute(sql: str, params: Optional[tuple] = None) -> int:
    """Execute an INSERT/UPDATE/DELETE query and return lastrowid when applicable."""
    with db_cursor() as cur:
        cur.execute(sql, params or ())
        try:
            return int(cur.lastrowid or 0)
        except Exception:
            return 0
