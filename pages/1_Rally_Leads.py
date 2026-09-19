import streamlit as st

from database import init_db, rows_for_table


st.set_page_config(page_title="Rally Leads", layout="wide")
init_db()

st.title("Rally Leads")
st.caption("Store dated snapshots of potential rally leads. Stats change, so snapshots are kept as separate records.")

rows = rows_for_table("player_snapshots")

if rows:
    st.dataframe([dict(row) for row in rows], use_container_width=True, hide_index=True)
else:
    st.info("No rally-lead snapshots yet.")

with st.expander("Planned fields"):
    st.write(
        "Snapshot code, player name, snapshot date, rally capacity, troop tier, "
        "troop-specific attack/defense/lethality/health, hero trio, and development notes."
    )
