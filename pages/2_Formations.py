import streamlit as st

from database import init_db, rows_for_table


st.set_page_config(page_title="Formations", layout="wide")
init_db()

st.title("Formations")
st.caption("Reusable hero, troop-ratio, and joiner-skill hypotheses to test.")

rows = rows_for_table("formations")

if rows:
    st.dataframe([dict(row) for row in rows], use_container_width=True, hide_index=True)
else:
    st.info("No formations yet.")

with st.expander("Planned fields"):
    st.write(
        "Formation code, name, purpose, hero trio, infantry/cavalry/archer percentages, "
        "four joiner skills, hypothesis, comparison group, priority, status, and notes."
    )
