from datetime import datetime

import streamlit as st

from database import init_db, kill_ratio, options_for, turret_bonus


st.set_page_config(page_title="Log Battle", layout="wide")
init_db()

st.title("Log Battle")
st.caption("Fast experiment entry. Keep this compact enough to use during testing.")

lead_options = options_for("player_snapshots", ["snapshot_code", "player_name"])
formation_options = options_for("formations", ["formation_code", "name"])

if not lead_options or not formation_options:
    st.warning("Add at least one rally-lead snapshot and one formation before logging battles.")

with st.form("battle_log_preview"):
    col1, col2, col3 = st.columns(3)
    battle_datetime = col1.datetime_input("Date/time", value=datetime.now())
    lead_label = col2.selectbox("Rally lead snapshot", list(lead_options.keys()), disabled=not lead_options)
    formation_label = col3.selectbox("Formation", list(formation_options.keys()), disabled=not formation_options)

    col1, col2, col3 = st.columns(3)
    battle_type = col1.selectbox("Battle type", ["Controlled", "Live KvK"])
    structure = col2.selectbox("Structure", ["Turret", "Castle"])
    role = col3.selectbox("Role", ["Attack", "Defense"])

    col1, col2, col3 = st.columns(3)
    opponent = col1.text_input("Opponent / defending lead")
    our_turrets = col2.number_input("Our turret count", min_value=0, max_value=4, value=0)
    enemy_turrets = col3.number_input("Enemy turret count", min_value=0, max_value=4, value=0)

    col1, col2, col3 = st.columns(3)
    result = col1.selectbox("Result", ["Win", "Loss"])
    our_casualties = col2.number_input("Our casualties", min_value=0, step=1)
    enemy_casualties = col3.number_input("Enemy casualties", min_value=0, step=1)

    notes = st.text_area("Notes / confounders")
    submitted = st.form_submit_button("Preview derived values")

if submitted:
    st.success("Form wiring is in place. Saving will be added in the next increment.")
    st.json(
        {
            "battle_datetime": battle_datetime.isoformat(),
            "rally_lead_snapshot": lead_label if lead_options else None,
            "formation": formation_label if formation_options else None,
            "battle_type": battle_type,
            "structure": structure,
            "role": role,
            "opponent": opponent,
            "our_turret_bonus": turret_bonus(our_turrets),
            "enemy_turret_bonus": turret_bonus(enemy_turrets),
            "result": result,
            "kill_ratio": kill_ratio(enemy_casualties, our_casualties),
            "notes": notes,
        }
    )
