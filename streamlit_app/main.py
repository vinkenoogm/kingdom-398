import streamlit as st

from streamlit_app.db import init_db
from streamlit_app.db.activity import get_active_activities
from streamlit_app.db.availability import save_availability, get_availability_slots
from streamlit_app.utils.authentication import upsert_player_and_check_pin


def render_slot_grid(
    slots: list[str],
    key_prefix: str,
    cols_per_row: int = 6,
    preselected_slots: list[str] | set[str] | None = None,
) -> list[str]:
    """
    Render a grid of checkboxes for the given time slots.

    Returns a list of selected slot strings.
    """
    selected: list[str] = []
    cols = []

    preselected = set(preselected_slots or [])

    for i, slot in enumerate(slots):
        # Start a new row every cols_per_row slots
        if i % cols_per_row == 0:
            cols = st.columns(cols_per_row)

        col = cols[i % cols_per_row]
        with col:
            checked = st.checkbox(
                slot,
                key=f"{key_prefix}_{slot}",
                value=slot in preselected
            )
        if checked:
            selected.append(slot)

    return selected



def run():
    st.set_page_config(page_title="Kingdom 398 events", page_icon="🎯")
    init_db()

    # Session state for player login
    if "player_id" not in st.session_state:
        st.session_state["player_id"] = None
        st.session_state["player_name"] = None

    st.title("Kingdom 398 events")

    # Player identification
    if st.session_state["player_id"] is None:
        st.subheader("Welcome! Who are you?")

        with st.form("identify_form"):
            game_username = st.text_input("In-game username")
            pin = st.text_input("PIN (optional, unless you've set it before)", type="password")
            user_game_id_str = st.text_input("In-game ID (8 numbers)")

            submitted_identify = st.form_submit_button("Continue")

        if submitted_identify:
            if not game_username:
                st.error("In-game username is required.")

            else:
                user_game_id = None
                if user_game_id_str:
                    try:
                        user_game_id = int(user_game_id_str)
                    except ValueError:
                        st.error("In-game ID must be a number.")
                        user_game_id = None

                success, msg, resolved_id = upsert_player_and_check_pin(
                    user_game_id=user_game_id,
                    game_username=game_username,
                    pin=pin or None,
                )
                if success:
                    st.session_state["player_id"] = resolved_id
                    st.session_state["player_name"] = game_username
                    st.success(msg)
                else:
                    st.session_state["player_id"] = None
                    st.session_state["player_name"] = None
                    st.error(msg)


    player_id = st.session_state["player_id"]
    player_name = st.session_state["player_name"]

    if player_id is not None and player_name is not None:
        # Show activities list
        activities = get_active_activities()
        if not activities:
            st.error("No active activities.")
            return

        st.subheader("Set availability")
        st.info(f"Using player ID {player_id}. Hi, **{player_name}**!")
        if st.button("Log out"):
            st.session_state["admin_id"] = None
            st.session_state["admin_name"] = None
            st.rerun()

        # Select activity
        activity_labels = []
        activity_ids = []
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

            # Fetch existing slots for this player & activity
            existing_slots = get_availability_slots(
                player_id=player_id,
                activity_id=selected_activity_id,
            )

            st.markdown("**When are you available?**")
            st.caption("Click all half-hour slots that work for you. All times are in UTC.")

            selected_slots = render_slot_grid(
                slots,
                key_prefix=f"slots_act_{selected_activity_id}",
                preselected_slots=existing_slots,
            )

            submitted_availability = st.form_submit_button("Save availability")

        if submitted_availability:
            save_availability(
                user_game_id=player_id,
                activity_id=selected_activity_id,
                slots=selected_slots,
            )
            st.success("Availability saved.")


if __name__ == "__main__":
    run()
