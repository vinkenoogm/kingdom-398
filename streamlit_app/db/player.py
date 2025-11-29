from datetime import datetime, UTC
from typing import Optional, Any
import pandas as pd
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
) -> int:
    """Create player and return new player_id."""
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
    return cur.lastrowid


def set_player_pin_hash(player_id: int, pin_hash: str) -> None:
    """Update player pin hash."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE player
        SET pin_hash = ?
        WHERE player_id = ?
        """,
        (pin_hash, player_id)
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
        "player_id",
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
        SELECT player_id, user_game_id, game_username, app_username, pin_hash, alliance, is_admin, is_super_admin, created_at
        FROM player
        WHERE {column} = ?
    """

    cur.execute(query, (value,))
    row = cur.fetchone()
    if row is None:
        return None

    return {
        "player_id": row[0],
        "user_game_id": row[1],
        "game_username": row[2],
        "app_username": row[3],
        "pin_hash": row[4],
        "alliance": row[5],
        "is_admin": int(row[6]),
        "is_super_admin": int(row[7]),
        "created_at": row[8],
    }

def update_players_from_df(changed: pd.DataFrame) -> int:
    """
    Applies updates to the database for the given rows, indexed by player_id.
    Returns the number of rows updated.
    """
    if changed.empty:
        return 0

    conn = get_connection()
    cur = conn.cursor()

    # Update only changed rows
    for player_id, row in changed.iterrows():
        cur.execute(
            """
            UPDATE player
            SET user_game_id = ?, game_username = ?, app_username = ?,
                alliance = ?,
                is_admin = ?, is_super_admin = ?
            WHERE player_id = ?
            """,
            (
                int(row["user_game_id"]) if pd.notna(row["user_game_id"]) else None,
                row["game_username"],
                row.get("app_username"),
                row.get("alliance"),
                int(bool(row["is_admin"])),
                int(bool(row["is_super_admin"])),
                int(player_id),
            ),
        )

    conn.commit()


def update_player_profile(
        player_id: int,
        user_game_id: int,
        game_username: str,
        app_username: str,
        alliance: str | None,
) -> None:
    """
    Update player profile for given player id.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE player
        SET user_game_id = ?, game_username = ?, app_username = ?, alliance = ?
        WHERE player_id = ?
        """,
        (user_game_id, game_username, app_username, alliance, player_id),
    )
    conn.commit()
