import streamlit as st

from streamlit_app.db import init_db
import streamlit as st

from streamlit_app.db import init_db
from streamlit_app.db.activity import get_active_activities
from streamlit_app.db.availability import save_availability
from streamlit_app.utils.authentication import upsert_player_and_check_pin


def run():
    st.set_page_config(page_title="Kingdom 398 events", page_icon="🎯")
    init_db()

    # Session state for player login
    if "player_id" not in st.session_state:
        st.session_state["player_id"] = None
        st.session_state["player_name"] = None

    st.title("Kingdom 398 events")

    # Player identification
    st.subheader("Welcome! Who are you?")

    with st.form("identify_form"):
        user_game_id_str = st.text_input("In-game ID (8 numbers)")
        game_username = st.text_input("In-game username")
        pin = st.text_input("PIN (optional, unless you've set it before)", type="password")

        submitted_identify = st.form_submit_button("Continue")

    if submitted_identify:
        if not user_game_id_str or not game_username:
            st.error("In-game ID and username are required.")
        else:
            try:
                user_game_id = int(user_game_id_str)
            except ValueError:
                st.error("In-game ID must be a number.")
            else:
                success, msg = upsert_player_and_check_pin(
                    user_game_id=user_game_id,
                    game_username=game_username,
                    pin=pin or None,
                )
                if success:
                    st.session_state["player_id"] = user_game_id
                    st.session_state["player_name"] = game_username
                    st.success(msg)
                else:
                    st.error(msg)

    player_id = st.session_state["player_id"]
    player_name = st.session_state["player_name"]

    # Show activities list
    activities = get_active_activities()
    if not activities:
        st.error("No active activities.")
        return

    st.subheader("Set availability")
    st.write(f"Using player ID {player_id}. Hi, {player_name}.")

    # Select activity
    activity_labels, activity_ids = []
    for activity_id, name, event_date in activities:
        label = f"{name} ({event_date})" if event_date else name
        activity_labels.append(label)
        activity_ids.append(activity_id)

    # Create half-hour slots
    # Todo: get possible slots from activity table
    slots = [f"{h:02d}:{m:02d}" for h in range(0, 24) for m in (0, 30)]

    with st.form("availability_form"):
        selected_activity_label = st.selectbox("Activity",
                                               options=activity_labels)
        activity_index = activity_labels.index(selected_activity_label)
        selected_activity_id = activity_ids[activity_index]

        selected_slots = st.multiselect(
            "When are you available? All times are in UTC.",
            options = slots,
            help = "Select all half-hour slots that work for you."
        )

        submitted_availability = st.form_submit_button("Save availability")

    if submitted_availability:
        save_availability(
            user_game_id=player_name,
            activity_id=selected_activity_id,
            slots=selected_slots,
        )
        st.success("Availability saved.")


if __name__ == "__main__":
    run()
