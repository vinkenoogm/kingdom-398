import streamlit as st

from database import init_db, rows_for_table


st.set_page_config(page_title="Results", layout="wide")
init_db()

st.title("Results")
st.caption("Browse logged experiments. Filtering and summaries come after battle saving is wired in.")

rows = rows_for_table("experiments")

if rows:
    st.dataframe([dict(row) for row in rows], use_container_width=True, hide_index=True)
else:
    st.info("No experiments logged yet.")
