import hashlib
from datetime import datetime, UTC

from streamlit_app.db import player as player_db


def hash_pin(pin: str) -> str:
    """Simple SHA256 hash to store pin"""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


def upsert_player_and_check_pin(
        user_game_id: int,
        game_username: str,
        pin: str | None,
) -> tuple[bool, str]:
    """
    Checks if player exists and enforces PIN rules.

    Returns (success, message)
    """
    player = player_db.get_player_by_id(user_game_id)
    now = datetime.now(UTC).isoformat(timespec="seconds")

    # Case 1: player does not exist in database, create new
    if not player:
        pin_hash = hash_pin(pin) if pin else None
        player_db.create_player(
            user_game_id=user_game_id,
            game_username=game_username,
            pin_hash=pin_hash,
            is_admin=False,
        )
        return True, "Player created."

    # Case 2: player exists in database without pin
    if not player["pin_hash"]:
        # If a pin is now provided, store in database
        if pin:
            new_pin_hash = hash_pin(pin)
            player_db.set_player_pin_hash(user_game_id, new_pin_hash)
            return True, f"Player {player['game_username']} existed without PIN, PIN now set."
        else:
            return True, f"Player {player['game_username']} exists without PIN. Availability can be updated."

    # Case 3: player has pin set, verify it
    if not pin:
        return False, f"{player['game_username']} has a PIN set, enter it to edit availability."

    if hash_pin(pin) != player["pin_hash"]:
        return False, "Incorrect PIN."

    # Allow editing if pin is correct
    return True, f"Logged in as {player['game_username']}."
