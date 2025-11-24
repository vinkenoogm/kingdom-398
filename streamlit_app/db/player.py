from datetime import datetime

from . import get_connection

def create_player(
        user_game_id: int,
        username: str,
        pin_hash: str,
        is_admin: bool = False
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO player (user_game_id, username, pin_hash, is_admin, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_game_id,
            username,
            pin_hash,
            int(is_admin),
            datetime.now(datetime.UTC).isoformat(timespec="seconds")
        ),
    )
    conn.commit()

def get_player_by_username(username: str) -> Optional[dict[str, Any]]:
    """Get player information from database by username, or None if not found."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_game_id, username, pin_hash, is_admin, created_at
        FROM player
        WHERE username = ?
        """,
        (username,),
    )
    row = cur.fetchone()
    if row is None:
        return None

    return {
        "user_game_id": row[0],
        "username": row[1],
        "pin_hash": row[2],
        "is_admin": int(row[3]),
        "created_at": row[4],
    }