import hashlib
import sqlite3
from typing import Optional

from streamlit_app.db import player as player_db


def hash_pin(pin: str) -> str:
    """Simple SHA256 hash to store pin"""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def find_player_by_login_name(name: str) -> Optional[dict]:
    """
    Find a player by login name. First look for app_username, then game_username.
    """
    if not name:
        return None

    player = player_db.get_player_by("app_username", name)
    if player:
        return player

    return player_db.get_player_by("game_username", name)


def check_player_pin(player_id: int, pin: str | None) -> tuple[bool, str]:
    """
    For an existing player, allow login if no pin is set, or if correct pin is provided.
    """
    player = player_db.get_player_by("player_id", player_id)
    if not player:
        return False, "Player not found."

    pin_hash = player["pin_hash"]

    if not pin_hash:
        return True, f"Logged in, no PIN set for player {player['game_username']}."

    if not pin:
        return False, f"{player['game_username']} has a PIN set, enter it to log in."

    if hash_pin(pin) != pin_hash:
        return False, f"Incorrect PIN."

    return True, "Logged in."


def register_new_player(
        user_game_id: int,
        game_username: str,
        pin: str | None,
) -> tuple[bool, str, Optional[int]]:
    """
    Create a new player with the given game_username and user_game_id and optional PIN.
    Returns (success, message, player_id or None)
    """
    if not game_username:
        return False, "In-game username is required."
    if not user_game_id:
        return False, "In-game user ID is required."

    pin_hash = hash_pin(pin) if pin else None

    try:
        player_id = player_db.create_player(
            user_game_id=user_game_id,
            game_username=game_username,
            app_username=None,
            pin_hash=pin_hash,
            is_admin=False,
            is_super_admin=False,
        )
    except sqlite3.IntegrityError as e:
        return False, f"Could not create player: {e}", None

    return True, "Player created", player_id


def authenticate_admin(app_username: str, pin: str) -> tuple[bool, str]:
    """
    Check admin login using app_username and pin.
    Returns (success, message).
    """
    if not app_username:
        return False, "Please enter your admin username."
    if not pin:
        return False, "Please enter your PIN."

    admin = player_db.get_player_by("app_username", app_username)

    if admin is None or not admin["is_admin"]:
        return False, "No admin account found with this username."
    if not admin["pin_hash"]:
        return False, "This admin account has no PIN yet (contact Finch)"
    if hash_pin(pin) != admin["pin_hash"]:
        return False, "Incorrect PIN."

    return True, f"Logged in as admin {admin['app_username']} ({admin['game_username']})"
