from datetime import datetime, UTC
from typing import Optional, Any

from . import get_connection


def any_admin_exists() -> bool:
    """Return True if there is at least one admin in the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM player WHERE is_admin = 1;")
    (count,) = cur.fetchone()
    return count > 0


def create_player(
        user_game_id: int,
        game_username: str,
        app_username: str | None,
        pin_hash: str | None,
        is_admin: bool = False,
        is_super_admin: bool = False,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO player (user_game_id, game_username, app_username, pin_hash, is_admin, is_super_admin, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_game_id,
            game_username,
            app_username,
            pin_hash,
            int(is_admin),
            int(is_super_admin),
            datetime.now(UTC).isoformat(timespec="seconds")
        ),
    )
    conn.commit()


def set_player_pin_hash(user_game_id: int, pin_hash: str) -> None:
    """Update player pin hash."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE player
        SET pin_hash = ?
        WHERE user_game_id = ?
        """,
        (pin_hash, user_game_id)
    )
    conn.commit()


def get_player_by(column: str, value: Any) -> Optional[dict[str, Any]]:
    """
    Player lookup by a given column.
    column: the column to filter on (e.g. 'game_username', 'user_game_id', 'app_username')
    value: the value to match in that column.
    """
    # whitelist column:
    allowed = {
        "game_username",
        "user_game_id",
        "app_username",
    }

    if column not in allowed:
        raise ValueError(f"Invalid lookup column: {column}")

    conn = get_connection()
    cur = conn.cursor()

    # Build the query dynamically but safely
    query = f"""
        SELECT user_game_id, game_username, app_username, pin_hash, is_admin, created_at
        FROM player
        WHERE {column} = ?
    """

    cur.execute(query, (value,))
    row = cur.fetchone()
    if row is None:
        return None

    return {
        "user_game_id": row[0],
        "game_username": row[1],
        "app_username": row[2],
        "pin_hash": row[3],
        "is_admin": int(row[4]),
        "created_at": row[5],
    }