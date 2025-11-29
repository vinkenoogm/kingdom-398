import hashlib
import sqlite3

from streamlit_app.db import player as player_db


def hash_pin(pin: str) -> str:
    """Simple SHA256 hash to store pin"""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def register_player(user_game_id_str: str, username: str, pin: str) -> tuple[bool, str]:
    """
    Try to register a new player in the database. Returns (success, message).
    If registration successful, returns (True, "")
    If unsuccessful, returns (False, error message)
    """
    try:
        user_game_id = int(user_game_id_str)
    except ValueError:
        return (False, "Your game ID must consist of numbers only.")

    if not username:
        return (False, "You must provide a username.")

    if not pin:
        return (False, "You must provide a pin.")

    pin_hash = hash_pin(pin)

    try:
        player_db.create_player(
            user_game_id=user_game_id,
            username=username,
            pin_hash=pin_hash,
            is_admin=False,
        )
    except sqlite3.IntegrityError:
        return (False, "Player with that game ID is already registered.")