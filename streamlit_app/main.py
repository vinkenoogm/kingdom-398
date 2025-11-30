import streamlit as st

from streamlit_app.db import init_db
from streamlit_app.db.activity import get_active_activities
from streamlit_app.db.availability import save_availability, get_availability_slots
from streamlit_app.db.player import get_player_by
from streamlit_app.utils.authentication import find_player_by_login_name, check_player_pin, \
    register_new_player




def run():
    st.set_page_config(page_title="Kingdom 398", page_icon="🎯")
    init_db()

    # Session state for player login
    if "player_id" not in st.session_state:
        st.session_state["player_id"] = None
        st.session_state["player_name"] = None

    if "login_stage" not in st.session_state:
        st.session_state["login_stage"] = "enter_username"

    if "login_candidate_player_id" not in st.session_state:
        st.session_state["login_candidate_player_id"] = None
        st.session_state["login_candidate_name"] = None

    st.title("Kingdom 398 events")

    # Log-in flow
    if st.session_state["player_id"] is None:
        stage = st.session_state["login_stage"]

        # STEP 1: Ask for username
        if stage == "enter_username":
            st.subheader("Welcome! Who are you?")
            st.caption("If you're here for the first time, enter your in-game username. If you're a returning user, you can use either your in-game username or app username, if you've set one.")

            with st.form("login_username_form"):
                login_name = st.text_input("Username")
                submitted = st.form_submit_button("Continue")

            if submitted:
                if not login_name.strip():
                    st.error("Username is required.")
                else:
                    player = find_player_by_login_name(login_name.strip())
                    if player:
                        st.session_state["login_stage"] = "existing_user"
                        st.session_state["login_candidate_player_id"] = player["player_id"]
                        st.session_state["login_candidate_name"] = login_name.strip()
                        st.rerun()
                    else:
                        st.session_state["login_stage"] = "new_user"
                        st.session_state["login_candidate_player_id"] = None
                        st.session_state["login_candidate_name"] = login_name.strip()
                        st.rerun()

        # STEP 2a: existing user, check for pin
        elif stage == "existing_user":
            candidate_name = st.session_state["login_candidate_name"]
            candidate_player_id = st.session_state["login_candidate_player_id"]

            st.subheader("Welcome back!")

            player = get_player_by("player_id", candidate_player_id)
            if not player:
                st.error("Could not load player from database. Please try again.")
                # reset flow
                st.session_state["login_stage"] = "enter_username"
                st.rerun()

            requires_pin = bool(player["pin_hash"])

            with st.form("login_existing_form"):
                st.text_input(
                    "Username",
                    value=candidate_name,
                    disabled=True,
                )

                if requires_pin:
                    pin = st.text_input("PIN", type="password")

                submitted = st.form_submit_button("Log in")

            if submitted:
                ok, msg = check_player_pin(candidate_player_id, pin or None)
                if ok:
                    st.session_state["player_id"] = candidate_player_id
                    st.session_state["player_name"] = player["game_username"]
                    # reset login flow state
                    st.session_state["login_stage"] = "enter_username"
                    st.session_state["login_candidate_player_id"] = None
                    st.session_state["login_candidate_name"] = None
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            st.button(
                "Not you? Choose a different username",
                on_click=lambda: (
                    st.session_state.update(
                        {
                            "login_stage": "enter_username",
                            "login_candidate_player_id": None,
                            "login_candidate_name": None,
                        }
                    )
                ),
            )

        # Step 2b: register new user
        elif stage == "new_user":
            candidate_name = st.session_state["login_candidate_name"]

            st.subheader("New player registration")
            st.caption(
                f"Couldn't find a player with username **{candidate_name}**. "
                "If you're new, register by adding your in-game ID and optional PIN below."
            )

            with st.form("register_new_player_form"):
                st.text_input(
                    "In-game username",
                    value=candidate_name,
                    disabled=True,
                )
                user_game_id_str = st.text_input("In-game ID (optional, 8 numbers)")
                pin = st.text_input(
                    "PIN (optional, to protect edits)",
                    type="password",
                )
                submitted = st.form_submit_button("Create player")

            if submitted:
                user_game_id = None
                if user_game_id_str.strip():
                    try:
                        user_game_id = int(user_game_id_str.strip())
                    except ValueError:
                        st.error("In-game ID must be a number.")
                        user_game_id = None
                        return

                if user_game_id is not None:
                    ok, msg, player_id = register_new_player(
                        user_game_id=user_game_id,
                        game_username=candidate_name,
                        pin=pin or None,
                    )
                    if ok and player_id is not None:
                        st.session_state["player_id"] = player_id
                        st.session_state["player_name"] = candidate_name

                        # Reset login flow state
                        st.session_state["login_stage"] = "enter_username"
                        st.session_state["login_candidate_player_id"] = None
                        st.session_state["login_candidate_name"] = None
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg or "Could not create player.")

    # End login flow

    st.write("Go to the activities page!")


if __name__ == "__main__":
    run()
