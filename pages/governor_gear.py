from pathlib import Path

import streamlit as st
import pandas as pd
from dataclasses import dataclass
import math  # NEW

LEVEL_OPTIONS = (
    [f"Green ({i} star)" for i in range(2)]
    + [f"Blue ({i} star)" for i in range(4)]
    + [f"Purple ({i} star)" for i in range(4)]
    + [f"Purple T1 ({i} star)" for i in range(4)]
    + [f"Gold ({i} star)" for i in range(4)]
    + [f"Gold T1 ({i} star)" for i in range(4)]
    + [f"Gold T2 ({i} star)" for i in range(4)]
    + [f"Gold T3 ({i} star)" for i in range(4)]
    + ["Red (0 star)"]
)

ITEMS_IN_ORDER = ["jacket", "pants", "ring", "staff", "crown", "necklace"]

CSV_PATH_DEFAULT = Path(__file__).resolve().parents[1] / "data" / "governor_gear_upgrades.csv"

# NEW: chest contents
CHEST_SATIN = 400
CHEST_THREADS = 4
CHEST_VISION = 1

def chests_needed(deficit: "Materials") -> int:
    """Minimum # of chests needed to cover deficit for the *next blocked step*."""
    if deficit is None:
        return 0
    need_s = math.ceil(deficit.satin / CHEST_SATIN) if deficit.satin > 0 else 0
    need_t = math.ceil(deficit.threads / CHEST_THREADS) if deficit.threads > 0 else 0
    need_v = math.ceil(deficit.vision / CHEST_VISION) if deficit.vision > 0 else 0
    return max(need_s, need_t, need_v)

def chest_overage(deficit: "Materials", n_chests: int) -> "Materials":
    """How much extra you’d have (beyond the deficit) if you add n chests."""
    return Materials(
        satin=n_chests * CHEST_SATIN - deficit.satin,
        threads=n_chests * CHEST_THREADS - deficit.threads,
        vision=n_chests * CHEST_VISION - deficit.vision,
    )

@dataclass(frozen=True)
class ExchangeRule:
    name: str
    give: dict[str, int]
    get: dict[str, int]
    max_times: int

EXCHANGES: list[ExchangeRule] = [
    ExchangeRule("5 threads -> 1 vision (max 5)", give={"threads": 5}, get={"vision": 1}, max_times=5),
    ExchangeRule("500 satin -> 1 vision (max 5)", give={"satin": 500}, get={"vision": 1}, max_times=5),
    ExchangeRule("1 vision -> 3 threads (max 500)", give={"vision": 1}, get={"threads": 3}, max_times=500),
    ExchangeRule("1 vision -> 300 satin (max 500)", give={"vision": 1}, get={"satin": 300}, max_times=500),
    ExchangeRule("10 threads -> 1 vision (max 50)", give={"threads": 10}, get={"vision": 1}, max_times=50),
    ExchangeRule("1 thread -> 50 satin (max 1000)", give={"threads": 1}, get={"satin": 50}, max_times=1000),
    ExchangeRule("1000 satin -> 1 vision (max 50)", give={"satin": 1000}, get={"vision": 1}, max_times=50),
    ExchangeRule("200 satin -> 1 thread (max 500)", give={"satin": 200}, get={"threads": 1}, max_times=500),
]

@dataclass
class Materials:
    satin: int
    threads: int
    vision: int

    def can_pay(self, cost: "Materials") -> bool:
        return (
            self.satin >= cost.satin
            and self.threads >= cost.threads
            and self.vision >= cost.vision
        )

    def pay(self, cost: "Materials") -> None:
        self.satin -= cost.satin
        self.threads -= cost.threads
        self.vision -= cost.vision

    def deficit_to_pay(self, cost: "Materials") -> "Materials":
        return Materials(
            satin=max(0, cost.satin - self.satin),
            threads=max(0, cost.threads - self.threads),
            vision=max(0, cost.vision - self.vision),
        )

    def as_dict(self):
        return {"Satin": self.satin, "Gilded Threads": self.threads, "Artisan's Vision": self.vision}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {}
    for c in df.columns:
        c_stripped = c.strip()
        lower = c_stripped.lower()
        if lower == "level":
            col_map[c] = "Level"
        elif lower in ["satin"]:
            col_map[c] = "Satin"
        elif lower in ["gilded threads", "gilded thread", "threads", "thread"]:
            col_map[c] = "Gilded Threads"
        elif lower in ["artisan's vision", "artisans vision", "artisan vision", "vision"]:
            col_map[c] = "Artisan's Vision"
    df = df.rename(columns=col_map)

    required = {"Level", "Satin", "Gilded Threads", "Artisan's Vision"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}. Found: {list(df.columns)}")
    return df


def build_cost_lookup(df: pd.DataFrame) -> dict[str, Materials]:
    lookup = {}
    for _, row in df.iterrows():
        lvl = str(row["Level"]).strip()
        lookup[lvl] = Materials(
            satin=int(row["Satin"]),
            threads=int(row["Gilded Threads"]),
            vision=int(row["Artisan's Vision"]),
        )
    return lookup


def next_level(current: str) -> str | None:
    if current not in LEVEL_OPTIONS:
        return None
    i = LEVEL_OPTIONS.index(current)
    if i >= len(LEVEL_OPTIONS) - 1:
        return None
    return LEVEL_OPTIONS[i + 1]


def simulate_upgrades(
    start_levels: dict[str, str],
    start_mats: Materials,
    cost_lookup: dict[str, Materials],
):
    levels = start_levels.copy()
    mats = Materials(start_mats.satin, start_mats.threads, start_mats.vision)

    upgrades_done = {k: 0 for k in levels.keys()}
    log_rows = []

    blocked = None

    round_idx = 0
    while True:
        round_idx += 1
        for item in ITEMS_IN_ORDER:
            cur = levels[item]
            nxt = next_level(cur)
            if nxt is None:
                blocked = (item, cur, None, None, None, "Reached max level")
                return levels, mats, upgrades_done, pd.DataFrame(log_rows), blocked

            if nxt not in cost_lookup:
                blocked = (item, cur, nxt, None, None, f"No cost row found in CSV for level '{nxt}'")
                return levels, mats, upgrades_done, pd.DataFrame(log_rows), blocked

            cost = cost_lookup[nxt]
            if not mats.can_pay(cost):
                deficit = mats.deficit_to_pay(cost)
                blocked = (item, cur, nxt, cost, deficit, "Insufficient materials")
                return levels, mats, upgrades_done, pd.DataFrame(log_rows), blocked

            mats.pay(cost)
            levels[item] = nxt
            upgrades_done[item] += 1

            log_rows.append(
                {
                    "Round": round_idx,
                    "Item": item,
                    "From": cur,
                    "To": nxt,
                    "Cost Satin": cost.satin,
                    "Cost Threads": cost.threads,
                    "Cost Vision": cost.vision,
                    "Remaining Satin": mats.satin,
                    "Remaining Threads": mats.threads,
                    "Remaining Vision": mats.vision,
                }
            )


# -----------------------
# UI
# -----------------------

st.title("Governor Gear Upgrade Planner")

st.subheader("Owned materials")
owned_satin = st.number_input("Satin", min_value=0, value=0, step=100)
owned_threads = st.number_input("Gilded Threads", min_value=0, value=0, step=1)
owned_vision = st.number_input("Artisan's Vision", min_value=0, value=0, step=1)

st.subheader("Current levels")
cols = st.columns(3)
level_inputs = {}

items_ui = ["crown", "necklace", "jacket", "pants", "ring", "staff"]
for idx, item in enumerate(items_ui):
    with cols[idx % 3]:
        level_inputs[item] = st.selectbox(
            f"{item.title()} level",
            options=["None"] + LEVEL_OPTIONS,  # (optional) include None in UI if you want
            index=0,
            key=f"lvl_{item}",
        )

try:
    df = pd.read_csv(CSV_PATH_DEFAULT)
    df = normalize_columns(df)
    cost_lookup = build_cost_lookup(df)
except Exception as e:
    st.error(f"Could not load/parse CSV: {e}")
    st.stop()

missing_levels = [lvl for lvl in LEVEL_OPTIONS if lvl not in cost_lookup]
if missing_levels:
    st.warning(
        "Some levels in LEVEL_OPTIONS have no matching row in the CSV. "
        "Upgrades may stop early when hitting one of these.\n\n"
        f"Missing examples: {missing_levels[:5]}{' ...' if len(missing_levels) > 5 else ''}"
    )

start_mats = Materials(int(owned_satin), int(owned_threads), int(owned_vision))
final_levels, leftover_mats, upgrades_done, log_df, blocked = simulate_upgrades(
    start_levels=level_inputs,
    start_mats=start_mats,
    cost_lookup=cost_lookup,
)

st.divider()
st.subheader("Result")

summary_df = pd.DataFrame(
    {
        "Item": items_ui,
        "Start Level": [level_inputs[i] for i in items_ui],
        "Final Level": [final_levels[i] for i in items_ui],
        "Upgrades Done": [upgrades_done[i] for i in items_ui],
    }
)
st.dataframe(summary_df, use_container_width=True)

st.markdown("**Leftover materials**")
st.dataframe(pd.DataFrame([leftover_mats.as_dict()]))

st.divider()
st.subheader("What blocks the next upgrade?")

item, from_lvl, to_lvl, cost, deficit, reason = blocked

if to_lvl is None:
    st.info(f"Stopped because **{item}** is already at max level ({from_lvl}).")
else:
    st.info(f"Stopped at **{item}**: {from_lvl} → {to_lvl} (**{reason}**)")

    if cost is not None and deficit is not None:
        st.markdown("**Cost of the blocked step**")
        st.dataframe(pd.DataFrame([cost.as_dict()]))

        st.markdown("**Minimum extra materials needed for that next step**")
        st.dataframe(pd.DataFrame([deficit.as_dict()]))

        # NEW: chest suggestion
        n = chests_needed(deficit)
        over = chest_overage(deficit, n)
        st.markdown("**Governor gear material chests needed (1 vision + 4 threads + 400 satin each)**")
        st.write(f"➡️ **{n} chest(s)**")
        st.caption(
            f"With {n} chest(s), you’d cover the deficit and have extra: "
            f"{over.satin} satin, {over.threads} threads, {over.vision} vision."
        )

st.divider()
with st.expander("Show upgrade log (every step)"):
    if log_df.empty:
        st.write("No upgrades were possible with the current materials.")
    else:
        st.dataframe(log_df, width="stretch")
