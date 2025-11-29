import streamlit as st

from streamlit_app.db import init_db
from streamlit_app.utils import authentication

def run()
    st.set_page_config(page_title="Kingdom 398 events", page_icon="🎯")

    init_db()

    st.title("Kingdom 398 events")
    st.subheader("Sign up")

    user_game_id = st.text_input("In-game user ID")
    username = st.text_input("In-game username")
    pin = st.text_input("Choose a PIN",
                        type="password")
    pin_confirm = st.text_input("Confirm PIN",
                                type="password")

    if st.button("Sign up"):
        if pin != pin_confirm:
            st.error("PINs do not match.")
        else:
            success, msg = authentication.register_player(
                user_game_id_str=user_game_id,
                username=username,
                pin=pin,
            )
            if success:
                st.success(msg)
            else:
                st.error(msg)