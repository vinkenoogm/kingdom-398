import re
from datetime import date

import streamlit as st
from sqlalchemy.exc import IntegrityError

from database import (
    create_player_snapshot,
    create_snapshot_heroes,
    heroes_for_snapshot,
    init_db,
    rows_for_table,
)


st.set_page_config(page_title="Rally Leads", layout="wide")
init_db()

st.title("Rally Leads")
st.caption("Store dated snapshots of potential rally leads. Stats change, so snapshots are kept as separate records.")


def default_snapshot_code(player_name: str, snapshot_date: date) -> str:
    name = re.sub(r"[^A-Za-z0-9]+", "-", player_name.strip()).strip("-").upper()
    if not name:
        return ""
    return f"{name}-{snapshot_date.isoformat()}"


def troop_inputs(prefix: str) -> dict[str, object]:
    col1, col2 = st.columns(2)
    return {
        f"{prefix}_troop_tier": col1.text_input("Troop tier", placeholder="T11", key=f"{prefix}_troop_tier"),
        f"{prefix}_truegold_level": col2.text_input("TrueGold level", placeholder="TG3", key=f"{prefix}_truegold_level"),
    }


with st.form("add_rally_lead"):
    st.subheader("Add Snapshot")

    col1, col2, col3 = st.columns(3)
    player_name = col1.text_input("Player name")
    snapshot_date = col2.date_input("Snapshot date", value=date.today())
    rally_capacity = col3.number_input("Rally capacity", min_value=0, step=1000)

    generated_code = default_snapshot_code(player_name, snapshot_date)
    st.caption(f"Snapshot code: {generated_code or 'enter a player name to generate'}")

    st.markdown("**Troop tiers**")
    inf_col, cav_col, arc_col = st.columns(3)
    with inf_col:
        st.caption("Infantry")
        infantry_stats = troop_inputs("infantry")
    with cav_col:
        st.caption("Cavalry")
        cavalry_stats = troop_inputs("cavalry")
    with arc_col:
        st.caption("Archers")
        archer_stats = troop_inputs("archer")

    st.markdown("**Available heroes**")
    hero_rows = st.data_editor(
        [
            {"hero_name": "Charles", "troop_type": "Infantry", "star_level": 0.0, "widget_level": 0, "notes": ""},
            {"hero_name": "Ava", "troop_type": "Cavalry", "star_level": 0.0, "widget_level": 0, "notes": ""},
            {"hero_name": "Wee & Woo", "troop_type": "Archers", "star_level": 0.0, "widget_level": 0, "notes": ""},
        ],
        column_config={
            "hero_name": st.column_config.TextColumn("Hero"),
            "troop_type": st.column_config.SelectboxColumn(
                "Troop type",
                options=["Infantry", "Cavalry", "Archers"],
                required=True,
            ),
            "star_level": st.column_config.NumberColumn(
                "Stars",
                min_value=0.0,
                max_value=5.0,
                step=0.1,
            ),
            "widget_level": st.column_config.NumberColumn(
                "Widget",
                min_value=0,
                max_value=10,
                step=1,
            ),
            "notes": st.column_config.TextColumn("Notes"),
        },
        num_rows="dynamic",
        hide_index=True,
        key="available_heroes",
    )

    development_notes = st.text_area("Development notes")
    submitted = st.form_submit_button("Save snapshot")

if submitted:
    final_snapshot_code = default_snapshot_code(player_name, snapshot_date)

    if not player_name.strip():
        st.error("Player name is required.")
    elif not final_snapshot_code:
        st.error("Snapshot code is required.")
    else:
        values = {
            "snapshot_code": final_snapshot_code,
            "player_name": player_name.strip(),
            "snapshot_date": snapshot_date.isoformat(),
            "rally_capacity": int(rally_capacity) if rally_capacity else None,
            "highest_troop_tier": "",
            **infantry_stats,
            **cavalry_stats,
            **archer_stats,
            "development_notes": development_notes.strip(),
        }
        try:
            snapshot_id = create_player_snapshot(values)
            hero_count = create_snapshot_heroes(snapshot_id, hero_rows)
            st.success(f"Saved rally-lead snapshot {final_snapshot_code} with {hero_count} available heroes.")
        except IntegrityError:
            st.error(f"Snapshot code already exists: {final_snapshot_code}")

rows = rows_for_table("player_snapshots")

st.subheader("Saved Snapshots")
if rows:
    display_rows = [
        {
            "Snapshot": row["snapshot_code"],
            "Player": row["player_name"],
            "Date": row["snapshot_date"],
            "Capacity": row["rally_capacity"],
            "Inf tier": row["infantry_troop_tier"],
            "Inf TG": row["infantry_truegold_level"],
            "Cav tier": row["cavalry_troop_tier"],
            "Cav TG": row["cavalry_truegold_level"],
            "Arch tier": row["archer_troop_tier"],
            "Arch TG": row["archer_truegold_level"],
            "Heroes saved": len(heroes_for_snapshot(row["id"])),
        }
        for row in rows
    ]
    st.dataframe(display_rows, use_container_width=True, hide_index=True)

    snapshot_options = {row["snapshot_code"]: row["id"] for row in rows}
    selected_snapshot_label = st.selectbox(
        "View available heroes for snapshot",
        options=list(snapshot_options.keys()),
    )
    hero_rows_for_snapshot = heroes_for_snapshot(snapshot_options[selected_snapshot_label])
    if hero_rows_for_snapshot:
        st.dataframe(
            [
                {
                    "Hero": row["hero_name"],
                    "Troop type": row["troop_type"],
                    "Stars": row["star_level"],
                    "Widget": row["widget_level"],
                    "Notes": row["notes"],
                }
                for row in hero_rows_for_snapshot
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No available heroes saved for this snapshot.")
else:
    st.info("No rally-lead snapshots yet.")
