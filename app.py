import streamlit as st

from database import DB_PATH, REPORTS_DIR, init_db


st.set_page_config(
    page_title="Kingshot Battle Strategy",
    page_icon="KS",
    layout="wide",
)

init_db()

st.title("Kingshot Battle Strategy")
st.caption("MVP workspace for rally leads, formations, battle logs, and results.")

st.write(
    "Use the pages in the sidebar to add rally-lead snapshots, define formations, "
    "log battle experiments, and browse results."
)

col1, col2 = st.columns(2)
col1.metric("Database", str(DB_PATH.relative_to(DB_PATH.parent.parent)))
col2.metric("Screenshots folder", str(REPORTS_DIR.relative_to(REPORTS_DIR.parent)))

st.info(
    "This first increment sets up the SQLite schema and Streamlit navigation. "
    "The next increment can flesh out add/edit forms and screenshot upload behavior."
)
