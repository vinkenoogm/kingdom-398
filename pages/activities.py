import streamlit as st

from streamlit_app.db.activity import get_active_activities
from streamlit_app.db.availability import save_availability, get_availability_slots


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

def main():
    st.set_page_config(page_title="Activities", page_icon="🎯")

    # Session state for player login
    if "player_id" not in st.session_state:
        st.session_state["player_id"] = None
        st.session_state["player_name"] = None

    player_id = st.session_state["player_id"]
    player_name = st.session_state["player_name"]

    # Logged in area
    if player_id is not None and player_name is not None:
        st.success(f"Hi, **{player_name}**!")
        if st.button("Log out", key="player_logout"):
            for key in ("player_id", "player_name"):
                st.session_state.pop(key, None)
            st.rerun()

        activities = get_active_activities()
        if not activities:
            st.error("No active activities.")
            return

        st.subheader("Set availability")

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
                player_id=player_id,
                activity_id=selected_activity_id,
                slots=selected_slots,
            )
            st.success("Availability saved.")

if __name__ == "__main__":
    main()