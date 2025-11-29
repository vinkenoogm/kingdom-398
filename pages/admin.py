import streamlit as st

from streamlit_app.db import init_db
from streamlit_app.db.activity import create_activity, get_all_activities
from streamlit_app.utils.authentication import authenticate_admin
from streamlit_app.db import player as player_db
from streamlit_app.db.export import get_table_df


def main():
    st.set_page_config(page_title="Kingshot 398 admin", page_icon="🔒")
    init_db()

    if "admin_id" not in st.session_state:
        st.session_state["admin_id"] = None
        st.session_state["admin_name"] = None

    st.title("Admin - Manage activities")

    if st.session_state["admin_id"] is None:
        st.subheader("Admin login")

        with st.form("admin_login_form"):
            app_username = st.text_input("Admin username")
            pin = st.text_input("PIN", type="password")
            submitted = st.form_submit_button("Log in")

        if submitted:
            ok, msg = authenticate_admin(app_username, pin)
            if ok:
                admin = player_db.get_player_by_app_username(app_username)
                st.session_state["admin_id"] = admin["user_game_id"]
                st.session_state["admin_name"] = admin["app_username"]
                st.success(msg)
            else:
                st.error(msg)

        if st.session_state["admin_id"] is None:
            return          # Not logged in, stop here

    ### LOGGED IN ADMIN AREA ###

    st.info(f"Logged in as admin user **{st.session_state['admin_name']}**")
    if st.button("Log out"):
        st.session_state["admin_id"] = None
        st.session_state["admin_name"] = None
        st.rerun()

    st.subheader("Add a new activity")
    with st.form("new_activity_form"):
        name = st.text_input("Activity name", help="e.g., Noble Advisor title")
        description = st.text_area("Description", help="Optional details for players", height=100)
        event_date = st.date_input("Event date", help="Pick the date for this activity")
        is_active = st.checkbox("Active", help="Players can give availability for active events only", value=True)

        submitted = st.form_submit_button("Create activity")

    if submitted:
        if not name:
            st.error("A name for the activity must be provided.")
        else:
            event_date_str = event_date.isoformat() if event_date else None
            create_activity(
                name=name,
                description=description,
                event_date=event_date_str,
                is_active=is_active
            )
            st.success(f"Activity **{name}** created successfully.")

    st.subheader("Existing activities")

    activities = get_all_activities()
    if not activities:
        st.info("No activities found.")
    else:
        st.table(
            [
                {
                    "ID": activity["id"],
                    "Name": activity["name"],
                    "Date": activity["event_date"],
                    "Active": "✅" if activity["is_active"] else "❌",
                    "Created at": activity["created_at"],
                }
                for activity in activities
            ]
        )

    st.subheader("Export data")

    st.caption("Download CSV snapshots of the current database tables.")

    col1, col2, col3 = st.columns(3)

    with col1:
        df_players = get_table_df("player")
        st.download_button(
            label="Download players.csv",
            data=df_players.to_csv(index=False).encode("utf-8"),
            file_name="players.csv",
            mime="text/csv",
        )

    with col2:
        df_activities = get_table_df("activity")
        st.download_button(
            label="Download activities.csv",
            data=df_activities.to_csv(index=False).encode("utf-8"),
            file_name="activities.csv",
            mime="text/csv",
        )

    with col3:
        df_availability = get_table_df("availability")
        st.download_button(
            label="Download availability.csv",
            data=df_availability.to_csv(index=False).encode("utf-8"),
            file_name="availability.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()