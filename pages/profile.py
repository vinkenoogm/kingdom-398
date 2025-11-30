import streamlit as st

from streamlit_app.db import init_db
from streamlit_app.db import player as player_db
from streamlit_app.utils.authentication import hash_pin


def main():
    st.set_page_config(page_title="Edit user profile", page_icon="👤")
    init_db()

    # Ensure session keys exist
    if "player_id" not in st.session_state:
        st.session_state["player_id"] = None
        st.session_state["player_name"] = None

    st.title("My profile")

    player_id = st.session_state["player_id"]
    player_name = st.session_state["player_name"]

    if player_id is None:
        st.info(
            "You're not logged in yet. Go to the **main page** to log in first, "
            "then come back here to edit your profile."
        )
        return

    st.success(f"Hi **{player_name}**!")

    if st.button("Log out", key="player_logout_profile"):
        for key in ("player_id", "player_name"):
            st.session_state.pop(key, None)
        st.rerun()

    player = player_db.get_player_by("player_id", player_id)
    if not player:
        st.error("Could not load your profile from the database.")
        return

    st.subheader("Edit your profile")

    with st.form("profile_form"):
        c1a, c2a = st.columns(2)
        with c1a:
            new_username = st.text_input(
                "In-game username",
                value=player["game_username"] or "",
            )
            new_alliance = st.text_input(
                "Alliance (optional)",
                value=player.get("alliance") or "",
            )

        with c2a:
            new_app_username = st.text_input(
                "App username (optional)",
                value=player["app_username"] or "",
                help="You can set a different username to use on this app, e.g., in case your in-game username is annoying to type.",
            )
            user_game_id_str = st.text_input(
                "In-game ID (8 numbers)",
                value=str(player["user_game_id"]) if player["user_game_id"] is not None else "",
            )

        st.markdown("**PIN settings**")
        st.caption(
            "Leave these blank to keep your current PIN. \n"
            "A PIN is required if you want to save your profile."
        )

        c1b, c2b = st.columns(2)
        with c1b:
            new_pin = st.text_input("New PIN", type="password")
        with c2b:
            new_pin_confirm = st.text_input("Confirm new PIN", type="password")

        submitted_profile = st.form_submit_button("Save profile")

    if not submitted_profile:
        return


    if not new_username.strip():
        st.error("In-game username cannot be empty.")
        return

    if not user_game_id_str.strip():
        st.error("In-game ID cannot be empty.")

    try:
        new_user_game_id = int(user_game_id_str.strip())
    except ValueError:
        st.error("In-game ID must be a number.")
        return

    # PIN logic
    if new_pin or new_pin_confirm:
        if new_pin != new_pin_confirm:
            st.error("New PIN and confirmation do not match.")
            return

    # Update database
    player_db.update_player_profile(
        player_id=player_id,
        user_game_id=new_user_game_id,
        game_username=new_username.strip(),
        app_username=new_app_username.strip(),
        alliance=new_alliance.strip() or None,
    )

    # PIN changes
    if new_pin:
        player_db.set_player_pin_hash(player_id, hash_pin(new_pin))

    # Keep session display name in sync
    st.session_state["player_name"] = new_username.strip()

    st.success("Profile updated.")
    st.rerun()


if __name__ == "__main__":
    main()
