import hashlib
import sqlite3

from streamlit_app.db import player as player_db


def hash_pin(pin: str) -> str:
    """Simple SHA256 hash to store pin"""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def upsert_player_and_check_pin(
        user_game_id: int,
        game_username: str,
        pin: str | None,
) -> tuple[bool, str, int | None]:
    """
    Checks if player exists and enforces PIN rules.

    Returns (success, message, resolved_player_id)
    """

    # Find player by username first
    player = player_db.get_player_by("game_username", game_username)

    print(player)

    # Case 1: player does not exist in database, create new
    if player is None:
        if not user_game_id:
            return False, "Unknown username, provide in-game ID to continue.", None

        pin_hash = hash_pin(pin) if pin else None

        try:
            new_player_id = player_db.create_player(
                user_game_id=user_game_id,
                game_username=game_username,
                app_username=None,
                pin_hash=pin_hash,
                is_admin=False,
            )
        except sqlite3.IntegrityError:
            # ID already in use or other constraint violation
            return False, "That in-game ID is already registered.", None

        return True, "Player created.", new_player_id

    resolved_id = player["player_id"]

    # Case 2: player exists in database without pin
    if not player["pin_hash"]:
        return True, f"Player {player['game_username']} exists without PIN.", resolved_id

    # Case 3: player has pin set, verify it
    if not pin:
        return False, f"{player['game_username']} has a PIN set, enter it to edit availability.", resolved_id

    if hash_pin(pin) != player["pin_hash"]:
        return False, "Incorrect PIN.", resolved_id

    # Allow editing if pin is correct
    return True, f"Logged in as {player['game_username']}.", resolved_id


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
