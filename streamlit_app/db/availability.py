from datetime import datetime, UTC

from . import get_connection


def save_availability(
        user_game_id: int,
        activity_id: int,
        slots: list[str],
) -> None:
    """
    Remove any previous saved slots for this (user, event) combination and save new.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM availability WHERE player_id = ? AND activity_id = ?",
        (user_game_id, activity_id),
    )

    now = datetime.now(UTC).isoformat(timespec="seconds")

    if slots:
        cur.executemany(
            """
            INSERT INTO availability (player_id, activity_id, slot, created_at)
            VALUES (?, ?, ?, ?) 
            """,
            [(user_game_id, activity_id, slot, now) for slot in slots]
        )

    conn.commit()
