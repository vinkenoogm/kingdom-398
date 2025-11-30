import streamlit as st

from streamlit_app.db import init_db
from streamlit_app.db import player as player_db
from streamlit_app.db.activity import create_activity, get_all_activities
from streamlit_app.db.export import get_table_df
from streamlit_app.utils.authentication import authenticate_admin, hash_pin


def main():
    st.set_page_config(page_title="Kingshot 398 admin", page_icon="🔒")
    init_db()

    if "admin_id" not in st.session_state:
        st.session_state["admin_id"] = None
        st.session_state["admin_name"] = None
        st.session_state["is_super_admin"] = False

    st.title("Admin - Manage activities")

    ### First time admin setup (ugh streamlit cloud)
    # Todo persistent database

    if not player_db.any_admin_exists():
        st.warning("No admin account exists yet. Setup the super admin.")

        with st.form("create_admin_form"):
            setup_token = st.text_input("Setup token", type="password")
            user_game_id_str = st.text_input("In-game ID")
            game_username = st.text_input("In-game username")
            app_username = st.text_input("Admin username", help="Can be the same as game username")
            pin = st.text_input("PIN", type="password")
            pin_confirm = st.text_input("Confirm PIN", type="password")

            submitted_setup = st.form_submit_button("Create admin account")

        if submitted_setup:
            expected_token = st.secrets.get("ADMIN_SETUP_TOKEN")
            if not expected_token:
                st.error("Server misconfigured: ADMIN_SETUP_TOKEN is missing in secrets.")
                return

            if setup_token != expected_token:
                st.error("Invalid setup token.")
                return

            if not user_game_id_str or not game_username or not app_username or not pin:
                st.error("Please fill out all fields.")
                return

            if pin != pin_confirm:
                st.error("PINs don't match.")
                return

            try:
                user_game_id = int(user_game_id_str)
            except ValueError:
                st.error("In-game ID must be a number.")
                return

            pin_hash = hash_pin(pin)

            try:
                player_db.create_player(
                    user_game_id=user_game_id,
                    game_username=game_username,
                    app_username=app_username,
                    pin_hash=pin_hash,
                    is_admin=True,
                    is_super_admin=True,
                )
            except Exception as e:
                st.error(f"Couldn't create admin, error: {e}")
                return

            st.success("Admin account created! Now login and do admin stuff")


    ### Admin login

    if st.session_state["admin_id"] is None:
        st.subheader("Admin login")

        with st.form("admin_login_form"):
            app_username = st.text_input("Admin username")
            pin = st.text_input("PIN", type="password")
            submitted = st.form_submit_button("Log in")

        if submitted:
            ok, msg = authenticate_admin(app_username, pin)
            if ok:
                admin = player_db.get_player_by("app_username", app_username)
                st.session_state["admin_id"] = admin["user_game_id"]
                st.session_state["admin_name"] = admin["app_username"]
                st.session_state["is_super_admin"] = bool(admin["is_super_admin"])
                st.rerun()
            else:
                st.error(msg)

        if st.session_state["admin_id"] is None:
            return          # Not logged in, stop here

    ### Logged in area

    st.info(f"Logged in as admin user **{st.session_state['admin_name']}**")
    if st.button("Log out", key="admin_logout"):
        for key in ("admin_id", "admin_name", "is_super_admin"):
            st.session_state.pop(key, None)
        st.rerun()

    with st.expander("Add a new activity"):
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

    # Super admin area
    if st.session_state.get("is_super_admin"):
        st.markdown("---")
        st.subheader("Super admin - player management")
        st.success(f"Hi {st.session_state.get("admin_name")} :)")

        df_players = get_table_df("player")

        if df_players.empty:
            st.info("No players found.")
        else:
            df_players = df_players.set_index("player_id")
            df_players['is_admin'] = df_players['is_admin'].astype("bool")
            editable_cols = ["game_username", "user_game_id", "app_username", "is_admin", "is_super_admin"]
            editable_cols = [c for c in editable_cols if c in df_players.columns]
            disabled_cols = [c for c in df_players.columns if c not in editable_cols]

            st.markdown("Edit players - caution!")
            st.caption("You can edit in-game username and ID, app usernames and admin status.")

            # Column order
            df_players = df_players[["game_username", "user_game_id", "alliance", "app_username", "is_admin", "is_super_admin", "created_at"]]

            edited_df = st.data_editor(
                df_players,
                num_rows="fixed",
                key="players_editor",
                disabled=disabled_cols,
            )

            if st.button("Save changes to player table"):
                old_df = df_players[editable_cols]
                new_df = edited_df[editable_cols]

                changed_rows = new_df.loc[(old_df != new_df).any(axis=1)]

                if changed_rows.empty:
                    st.info("No changes made.")
                else:
                    n_updated = player_db.update_players_from_df(changed_rows)
                    st.success(f"Saved changes for {n_updated} player{'s' if n_updated != 1 else ''}.")
                    st.rerun()

if __name__ == "__main__":
    main()