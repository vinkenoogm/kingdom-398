from datetime import datetime, UTC
from typing import Any

from . import get_connection


def get_active_activities() -> list[tuple[int, str, str | None]]:
    """
    Returns a list of (id, name, event_date) for active activities.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, event_date 
        FROM activity
        WHERE is_active = 1
        ORDER BY event_date ASC
        """
    )
    rows: list[tuple[int, str, str | None]] = cur.fetchall()
    return rows


def create_activity(
        name: str,
        description: str | None,
        event_date: str | None,     # "YY-MM-DD" or None
        is_active: bool = True,
) -> None:
    """Add a new activity to the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO activity (name, description, event_date, is_active, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name,
         description,
         event_date, int(is_active),
         datetime.now(UTC).isoformat(timespec="seconds")),
    )


def get_all_activities() -> list[dict[str, Any]]:
    """Return all activities with full info."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, description, event_date, is_active, created_at
        FROM activity
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    result: list[dict[str, Any]] = []
    for row in rows:
        result.append(
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "event_date": row[3],
                "is_active": row[4],
                "created_at": row[5],
            }
        )
    return result
