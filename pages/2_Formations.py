import streamlit as st
from sqlalchemy.exc import IntegrityError

from database import create_formation, init_db, rows_for_table, seed_default_formations


st.set_page_config(page_title="Formations", layout="wide")
init_db()

st.title("Formations")
st.caption("Reusable hero, troop-ratio, and joiner-skill hypotheses to test.")

if st.button("Seed default Gen 7 test formations"):
    inserted = seed_default_formations()
    if inserted:
        st.success(f"Added {inserted} default formations.")
    else:
        st.info("Default formations already exist.")

with st.form("add_formation"):
    st.subheader("Add Formation")

    col1, col2, col3, col4 = st.columns(4)
    formation_code = col1.text_input("Formation code", placeholder="ATK-01")
    name = col2.text_input("Name", placeholder="Charles / Ava / Wee & Woo")
    purpose = col3.selectbox("Purpose", ["Attack", "Defense"])
    status = col4.selectbox("Status", ["Planned", "Testing", "Promising", "Proven", "Dropped"])

    col1, col2, col3, col4 = st.columns(4)
    infantry_pct = col1.number_input("Infantry %", min_value=0, max_value=100, value=50)
    cavalry_pct = col2.number_input("Cavalry %", min_value=0, max_value=100, value=20)
    archer_pct = col3.number_input("Archer %", min_value=0, max_value=100, value=30)
    priority = col4.number_input("Priority", min_value=1, max_value=5, value=3)

    ratio_total = infantry_pct + cavalry_pct + archer_pct
    if ratio_total == 100:
        st.caption("Troop ratio total: 100%")
    else:
        st.warning(f"Troop ratio total is {ratio_total}%. It must be 100%.")

    st.markdown("**Hero trio**")
    col1, col2, col3 = st.columns(3)
    infantry_hero = col1.text_input("Infantry hero", placeholder="Charles")
    cavalry_hero = col2.text_input("Cavalry hero", placeholder="Ava")
    archer_hero = col3.text_input("Archer hero", placeholder="Wee & Woo")

    st.markdown("**Joiner skills**")
    col1, col2, col3, col4 = st.columns(4)
    joiner_skill_1 = col1.text_input("Skill 1", placeholder="Chenko")
    joiner_skill_2 = col2.text_input("Skill 2", placeholder="Chenko")
    joiner_skill_3 = col3.text_input("Skill 3", placeholder="Amane")
    joiner_skill_4 = col4.text_input("Skill 4", placeholder="Amane")

    comparison_group = st.text_input("Comparison group", placeholder="Troop ratio test A")
    hypothesis = st.text_area("Hypothesis")
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Save formation")

if submitted:
    if not formation_code.strip():
        st.error("Formation code is required.")
    elif not name.strip():
        st.error("Formation name is required.")
    elif ratio_total != 100:
        st.error("Infantry, cavalry, and archer percentages must add to 100.")
    else:
        values = {
            "formation_code": formation_code.strip(),
            "name": name.strip(),
            "purpose": purpose,
            "infantry_hero": infantry_hero.strip(),
            "cavalry_hero": cavalry_hero.strip(),
            "archer_hero": archer_hero.strip(),
            "infantry_pct": int(infantry_pct),
            "cavalry_pct": int(cavalry_pct),
            "archer_pct": int(archer_pct),
            "joiner_skill_1": joiner_skill_1.strip(),
            "joiner_skill_2": joiner_skill_2.strip(),
            "joiner_skill_3": joiner_skill_3.strip(),
            "joiner_skill_4": joiner_skill_4.strip(),
            "hypothesis": hypothesis.strip(),
            "comparison_group": comparison_group.strip(),
            "priority": int(priority),
            "status": status,
            "notes": notes.strip(),
        }
        try:
            create_formation(values)
            st.success(f"Saved formation {formation_code.strip()}.")
        except IntegrityError:
            st.error(f"Formation code already exists: {formation_code.strip()}")

rows = rows_for_table("formations")

st.subheader("Saved Formations")
if rows:
    display_rows = [
        {
            "Code": row["formation_code"],
            "Name": row["name"],
            "Purpose": row["purpose"],
            "Ratio": f"{row['infantry_pct']} / {row['cavalry_pct']} / {row['archer_pct']}",
            "Heroes": f"{row['infantry_hero']} / {row['cavalry_hero']} / {row['archer_hero']}",
            "Comparison": row["comparison_group"],
            "Priority": row["priority"],
            "Status": row["status"],
        }
        for row in rows
    ]
    st.dataframe(display_rows, use_container_width=True, hide_index=True)
else:
    st.info("No formations yet.")
