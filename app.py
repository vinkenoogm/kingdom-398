import streamlit as st

from database import database_label, init_db
from storage import storage_label


st.set_page_config(
    page_title="Kingshot Battle Strategy",
    page_icon="KS",
    layout="wide",
)

init_db()

st.title("Kingshot Battle Strategy")
st.caption("MVP workspace for rally leads, formations, battle logs, and results.")

st.write("Use the sidebar pages in this order:")

st.markdown(
    """
1. **Rally Leads**: save dated snapshots of each potential rally lead. These hold stable account context such as troop tiers, TrueGold levels, rally capacity, and available heroes.
2. **Formations**: save reusable test setups. These hold the hero trio, troop ratio, joiner skills, and hypothesis you want to test.
3. **Log Battle**: record one battle experiment by selecting a rally lead snapshot and formation, then entering the battle-report stats, troop totals, troops remaining, outcome, opponent info, and optional screenshots.
4. **Results**: browse saved experiments and compare outcomes across leads, formations, opponents, and structures.

App will be updated with more features to compare battle outcomes across different rally leads, formations, and defensive setups!
"""
)

st.info(
    "Rally leads and formations are stored separately on purpose. A single rally lead can test many formations, "
    "and a single formation can be tested with different leads or against different defensive setups."
)

col1, col2 = st.columns(2)
col1.metric("Database", database_label())
col2.metric("Screenshots", storage_label())
