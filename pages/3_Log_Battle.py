from datetime import datetime

import streamlit as st

from database import (
    create_experiment,
    create_screenshot_record,
    init_db,
    kill_ratio,
    options_for,
    turret_bonus,
)
from storage import save_uploaded_file


st.set_page_config(page_title="Log Battle", layout="wide")
init_db()

st.title("Log Battle")
st.caption("Fast experiment entry. Keep this compact enough to use during testing.")

lead_options = options_for("player_snapshots", ["snapshot_code", "player_name"])
formation_options = options_for("formations", ["formation_code", "name"])

if not lead_options or not formation_options:
    st.warning("Add at least one rally-lead snapshot and one formation before logging battles.")


def report_stat_inputs(prefix: str, key_prefix: str = "report") -> dict[str, float]:
    return {
        f"{key_prefix}_{prefix}_attack": st.number_input(
            "Attack %",
            min_value=0.0,
            step=0.1,
            format="%.2f",
            key=f"{key_prefix}_{prefix}_attack",
        ),
        f"{key_prefix}_{prefix}_defense": st.number_input(
            "Defense %",
            min_value=0.0,
            step=0.1,
            format="%.2f",
            key=f"{key_prefix}_{prefix}_defense",
        ),
        f"{key_prefix}_{prefix}_lethality": st.number_input(
            "Lethality %",
            min_value=0.0,
            step=0.1,
            format="%.2f",
            key=f"{key_prefix}_{prefix}_lethality",
        ),
        f"{key_prefix}_{prefix}_health": st.number_input(
            "Health %",
            min_value=0.0,
            step=0.1,
            format="%.2f",
            key=f"{key_prefix}_{prefix}_health",
        ),
    }


def save_uploaded_screenshots(experiment_id: int, experiment_code: str, uploads: list) -> int:
    saved = 0
    for index, upload in enumerate(uploads, start=1):
        file_path = save_uploaded_file(upload, experiment_code, index)
        create_screenshot_record(experiment_id, file_path, upload.name)
        saved += 1
    return saved


def derive_casualties(total: int, remaining: int) -> int | None:
    if not total:
        return None
    return max(total - remaining, 0)


st.subheader("Battle Setup")
col1, col2, col3 = st.columns(3)
now = datetime.now()
battle_date = col1.date_input("Date", value=now.date())
battle_time = col1.time_input("Time", value=now.time().replace(microsecond=0))
lead_label = col2.selectbox(
    "Rally lead snapshot",
    list(lead_options.keys()) or ["Add a rally lead first"],
    disabled=not lead_options,
)
formation_label = col3.selectbox(
    "Formation",
    list(formation_options.keys()) or ["Add a formation first"],
    disabled=not formation_options,
)

col1, col2, col3 = st.columns(3)
battle_type = col1.selectbox("Battle type", ["Controlled", "Live KvK"])
structure = col2.selectbox("Structure", ["Non-castle", "Castle"])
role = col3.selectbox("Role", ["Attack", "Defense"])

opponent = st.text_input("Opponent / defending lead")
opponent_source = st.radio(
    "Opponent info",
    ["New / from report", "Known snapshot + formation"],
    horizontal=True,
)

enemy_snapshot_id = None
enemy_formation_id = None
opponent_formation_summary = ""

if opponent_source == "Known snapshot + formation":
    col1, col2 = st.columns(2)
    enemy_lead_label = col1.selectbox(
        "Enemy rally lead snapshot",
        list(lead_options.keys()) or ["Add a rally lead first"],
        disabled=not lead_options,
    )
    enemy_formation_label = col2.selectbox(
        "Enemy formation",
        list(formation_options.keys()) or ["Add a formation first"],
        disabled=not formation_options,
    )
    if lead_options:
        enemy_snapshot_id = lead_options[enemy_lead_label]
    if formation_options:
        enemy_formation_id = formation_options[enemy_formation_label]
else:
    opponent_formation_summary = st.text_input(
        "Opponent formation from report",
        placeholder="Charles / Ava / Wee & Woo, 50 / 20 / 30",
    )

if structure == "Castle":
    col1, col2 = st.columns(2)
    our_turrets = col1.number_input("Our turret count", min_value=0, max_value=4, value=0)
    enemy_turrets = col2.number_input("Enemy turret count", min_value=0, max_value=4, value=0)
else:
    our_turrets = 0
    enemy_turrets = 0

st.subheader("Battle Report")
col1, col2 = st.columns(2)
our_total_troops = col1.number_input("Our total troops", min_value=0, step=1)
enemy_total_troops = col2.number_input("Enemy total troops", min_value=0, step=1)

st.markdown("**Our report stats**")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Infantry")
    infantry_report_stats = report_stat_inputs("infantry")
with col2:
    st.caption("Cavalry")
    cavalry_report_stats = report_stat_inputs("cavalry")
with col3:
    st.caption("Archers")
    archer_report_stats = report_stat_inputs("archer")

st.markdown("**Enemy report stats**")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Infantry")
    enemy_infantry_report_stats = report_stat_inputs("infantry", "enemy_report")
with col2:
    st.caption("Cavalry")
    enemy_cavalry_report_stats = report_stat_inputs("cavalry", "enemy_report")
with col3:
    st.caption("Archers")
    enemy_archer_report_stats = report_stat_inputs("archer", "enemy_report")

uploads = st.file_uploader(
    "Battle report screenshots",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

st.subheader("Outcome")
col1, col2, col3 = st.columns(3)
result = col1.selectbox("Result", ["Win", "Loss"])
our_remaining_troops = col2.number_input("Our troops remaining", min_value=0, step=1)
enemy_remaining_troops = col3.number_input("Enemy troops remaining", min_value=0, step=1)
notes = st.text_area("Notes / confounders")

submitted = st.button(
    "Save battle",
    disabled=not lead_options or not formation_options,
    type="primary",
)

if submitted:
    battle_datetime = datetime.combine(battle_date, battle_time)
    our_casualties = derive_casualties(int(our_total_troops), int(our_remaining_troops))
    enemy_casualties = derive_casualties(int(enemy_total_troops), int(enemy_remaining_troops))
    experiment_values = {
        "battle_datetime": battle_datetime.isoformat(),
        "player_snapshot_id": lead_options[lead_label],
        "formation_id": formation_options[formation_label],
        "enemy_player_snapshot_id": enemy_snapshot_id,
        "enemy_formation_id": enemy_formation_id,
        "opponent_source": opponent_source,
        "battle_type": battle_type,
        "structure": structure,
        "role": role,
        "opponent": opponent.strip(),
        "opponent_formation_summary": opponent_formation_summary.strip(),
        "our_total_troops": int(our_total_troops) if our_total_troops else None,
        "enemy_total_troops": int(enemy_total_troops) if enemy_total_troops else None,
        "our_remaining_troops": int(our_remaining_troops) if our_total_troops else None,
        "enemy_remaining_troops": int(enemy_remaining_troops) if enemy_total_troops else None,
        "our_turret_count": int(our_turrets),
        "enemy_turret_count": int(enemy_turrets),
        "our_turret_bonus": turret_bonus(our_turrets),
        "enemy_turret_bonus": turret_bonus(enemy_turrets),
        "result": result,
        "our_casualties": our_casualties,
        "enemy_casualties": enemy_casualties,
        "kill_ratio": kill_ratio(enemy_casualties, our_casualties),
        **infantry_report_stats,
        **cavalry_report_stats,
        **archer_report_stats,
        **enemy_infantry_report_stats,
        **enemy_cavalry_report_stats,
        **enemy_archer_report_stats,
        "notes": notes.strip(),
    }
    experiment_id, experiment_code = create_experiment(experiment_values)
    screenshot_count = save_uploaded_screenshots(experiment_id, experiment_code, uploads)
    st.success(f"Saved {experiment_code} with {screenshot_count} screenshot(s).")
