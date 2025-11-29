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

