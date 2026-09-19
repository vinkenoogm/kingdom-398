# Kingshot Battle Strategy App

## Project goal

Build a small Streamlit app to help our Kingshot battle strategy team systematically test rally leads, hero combinations, troop formations, and joiner skill combinations during Castle Battle / Kingdom of Power (KvK).

The core goal is **not** to build a general Kingshot database or simulator. We want a practical tool that makes it easy to:

1. Store information about our strongest potential rally leads.
2. Define reusable hero/troop formations we want to test.
3. Log battle experiments quickly during controlled tests or real KvK.
4. Attach battle-report screenshots.
5. Compare formations/rally leads later based on actual outcomes.
6. Eventually extract data automatically from battle-report screenshots.

The main design principle is:

> Collect enough information to interpret experiments, but keep battle logging fast enough that people will actually use it.

---

# Relevant Kingshot battle mechanics

Our kingdom is currently on **Generation 7 heroes**.

For rally combat:

* The **rally lead** supplies the important account-wide combat stats, including troop combat stats, research, Governor Gear, charms, hero development, widgets, etc.
* The rally lead uses **three heroes**, one per troop type.
* Rally joiners mainly contribute troops.
* Joiners can also contribute up to **four first-hero expedition skills**, depending on skill level / join order.
* Therefore rally strength is not adequately represented by total account power.
* We care particularly about troop-specific:

  * Attack
  * Defense
  * Lethality
  * Health

There are three troop types:

* Infantry
* Cavalry
* Archers

Important combat concepts:

* Infantry > Cavalry > Archers > Infantry as troop counters.
* Infantry function largely as the frontline.
* Cavalry can sometimes bypass the frontline and attack Archers.
* Archers can deal very high damage and may attack twice.
* This means troop ratios matter substantially.

Common formation ratios worth testing include:

* 50 / 20 / 30
* 50 / 10 / 40
* 48 / 4 / 48
* 50 / 0 / 50

These are **candidate formations to test**, not assumed truths.

For Gen 7, important heroes include:

* Charles — Infantry, strongly defense-oriented.
* Ava — Cavalry, strongly offensive/rally-oriented.
* Wee & Woo — Archer, strongly offensive.

One interesting experiment is therefore comparing different Infantry heroes while holding Ava + Wee & Woo constant.

Possible Infantry candidates include:

* Charles
* Triton
* Amadeus

We also want to test joiner-skill packages such as:

* 4 × Chenko
* 2 × Chenko + 2 × Amane

Again, these should be treated as hypotheses, not fixed meta.

---

# Castle vs turret testing

We think **turrets are probably better for controlled experiments** than the Castle.

Castle battles can contain additional noise such as:

* Turret bombardment against the Castle.
* Rapidly changing Castle garrisons.
* Double-rally timing.
* Different kingdom-wide turret buffs.

During KvK, turret ownership gives a kingdom Squad Lethality bonuses approximately:

* 0 turrets = 0%
* 1 turret = 8%
* 2 turrets = 12%
* 3 turrets = 15%
* 4 turrets = 20%

Therefore every battle test should record:

* Our turret count
* Enemy turret count

We want to distinguish:

* **Controlled test**
* **Live KvK battle**

and:

* **Turret**
* **Castle**

Controlled turret tests are preferred for comparing formations.

Castle fights are useful later for validating whether a setup works in the real battle environment.

---

# App architecture

Use:

* Python
* Streamlit
* SQLite

Keep the architecture simple.

Suggested project structure:

```text
kingdom-398/
│
├── app.py
├── database.py
├── models.py              # optional
├── pages/
│   ├── 1_Rally_Leads.py
│   ├── 2_Formations.py
│   ├── 3_Log_Battle.py
│   └── 4_Results.py
│
├── data/
│   └── kingshot.db
│
├── battle_reports/
│
├── PROJECT_CONTEXT.md
└── requirements.txt
```

Avoid unnecessary frameworks or infrastructure.

SQLite should be sufficient.

---

# Main pages

## 1. Rally Leads

Purpose:

Store snapshots of our strongest potential rally leads.

Important: player stats change over time, so ideally use **snapshots**, not one mutable permanent row.

Example snapshot ID:

```text
FINCH-2026-09-19
```

Minimum useful fields:

* Player name
* Snapshot date
* Rally capacity
* Highest troop tier / TrueGold level

Infantry:

* Attack
* Defense
* Lethality
* Health

Cavalry:

* Attack
* Defense
* Lethality
* Health

Archer:

* Attack
* Defense
* Lethality
* Health

Heroes:

* Infantry hero
* Cavalry hero
* Archer hero

Optional development notes:

* stars
* skill level
* widget level
* unusually strong/weak hero development
* important pets/research/buffs if relevant

Do NOT initially require detailed individual Governor Gear pieces or 18 individual charm entries.

The resulting combat stats are more useful than recording every source of those stats.

Optional derived metrics:

```text
Offense index = (1 + Attack) × (1 + Lethality)

Survival index = (1 + Defense) × (1 + Health)
```

Use these only as comparative summaries, not as claims about the exact Kingshot damage engine.

---

# 2. Formations

Purpose:

Store reusable candidate formations/hypotheses.

Suggested fields:

* Formation ID
* Name
* Purpose

  * Attack
  * Defense
* Infantry hero
* Cavalry hero
* Archer hero
* Infantry %
* Cavalry %
* Archer %
* Joiner skill 1
* Joiner skill 2
* Joiner skill 3
* Joiner skill 4
* Hypothesis
* Comparison group
* Priority
* Status

  * Planned
  * Testing
  * Promising
  * Proven
  * Dropped
* Notes

Examples:

```text
ATK-01
Charles / Ava / Wee & Woo
50 / 20 / 30
```

```text
ATK-02
Charles / Ava / Wee & Woo
50 / 10 / 40
```

```text
ATK-03
Charles / Ava / Wee & Woo
48 / 4 / 48
```

```text
ATK-04
Charles / Ava / Wee & Woo
50 / 0 / 50
```

A comparison group can link formations intended for direct comparison, e.g.:

```text
Troop ratio test A
```

---

# 3. Log Battle

This is the most important page.

The UI should be optimized for **fast entry during battle testing**.

Do NOT expose dozens of fields.

Prefer dropdowns and defaults wherever possible.

Core inputs:

* Date/time
* Rally lead snapshot
* Formation
* Battle type

  * Controlled
  * Live KvK
* Structure

  * Turret
  * Castle
* Role

  * Attack
  * Defense
* Opponent / defending lead
* Our turret count
* Enemy turret count
* Result

  * Win
  * Loss
* Our casualties
* Enemy casualties
* Notes / confounders
* Screenshot upload

The formation selection should automatically provide:

* hero trio
* Infantry/Cavalry/Archer ratio
* joiner skill package

The rally-lead selection should automatically reference the saved player stats.

Derived automatically:

* Our turret lethality bonus
* Enemy turret lethality bonus
* Kill ratio

Example:

```text
Kill ratio = enemy casualties / our casualties
```

Handle divide-by-zero safely.

Possible confounder notes:

* Enemy garrison changed
* Temporary buff active
* Double rally
* Previous rally landed seconds earlier
* Castle bombardment
* Opponent changed heroes
* Incorrect joiner hero
* Rally not full

Optional later improvement:

A **Duplicate Previous Test** button.

Typical workflow:

1. Log test with 50/20/30.
2. Duplicate test.
3. Change formation to 50/10/40.
4. Enter new result.
5. Repeat.

This is especially useful for controlled turret testing.

---

# 4. Results

Initial version should stay simple.

Show experiment table with filters:

* Rally lead
* Formation
* Structure
* Controlled / live
* Attack / defense
* Opponent
* Date
* Win/loss

Useful summary metrics:

* Number of tests
* Wins
* Win rate
* Median kill ratio
* Mean kill ratio
* Our average casualties
* Enemy average casualties

Useful comparisons:

* Formation vs formation
* Rally lead vs rally lead
* Same lead + different troop ratio
* Same formation + different joiner package

For controlled analyses, allow filtering to:

```text
Controlled tests only
```

and ideally:

```text
Same opponent
Same structure
Same turret-buff situation
```

Charts can come after basic data entry works.

---

# Screenshots

Version 1:

When logging a battle, allow screenshot upload.

Save the screenshot locally, for example:

```text
battle_reports/EXP-0042_1.png
```

Store the filepath in the SQLite database.

Ideally allow more than one screenshot per experiment because Kingshot battle reports may have multiple screens containing useful information.

The original screenshot should always remain available even if values are entered manually.

---

# Future screenshot extraction

Do NOT implement screenshot interpretation in the initial MVP.

Future workflow:

1. Upload battle report screenshot.
2. App extracts candidate values.
3. Show extracted values in editable fields.
4. User verifies/corrects them.
5. Save confirmed values.

Potential fields to extract later:

* attacker
* defender
* hero trio
* troop composition
* troop counts
* casualties
* combat stats
* win/loss
* troop-type casualty breakdown

The screenshot dataset collected during normal use can later be used to test extraction reliability.

Never silently trust OCR/extraction; require confirmation.

---

# Database concept

Likely tables:

```text
player_snapshots
formations
experiments
screenshots
```

Possible relationships:

```text
player_snapshots
    1
    |
    └── many experiments

formations
    1
    |
    └── many experiments

experiments
    1
    |
    └── many screenshots
```

Avoid premature normalization.

We can add hero/reference tables later if needed.

---

# UX principles

This app will sometimes be used during active KvK coordination.

Therefore:

* Minimize typing.
* Prefer selectboxes.
* Use sensible defaults.
* Do not require optional information.
* Keep the Log Battle form compact.
* Automatically calculate values where possible.
* Use clear Save confirmation.
* Make it hard to accidentally lose an entered experiment.
* Allow editing/deleting incorrect experiments.
* Use wide Streamlit layout where useful.
* Keep styling clean rather than elaborate.

Target: logging one experiment should require roughly **6–10 actual user inputs**, not 30–40.

---

# MVP scope

Build these first:

1. SQLite initialization.
2. Add/edit Rally Lead snapshots.
3. Add/edit Formations.
4. Log Experiment.
5. Upload screenshot(s).
6. Automatically calculate turret buffs.
7. Automatically calculate kill ratio.
8. Browse/filter experiments.
9. Edit/delete incorrect entries.

Then add:

10. Duplicate previous experiment.
11. Summary metrics.
12. Basic charts.
13. CSV/Excel export.

Later only:

* Screenshot/OCR interpretation.
* Automatic hero database.
* Advanced battle simulation.
* Authentication.
* Multi-user hosted database.
* Statistical modelling.

---

# Development philosophy

Keep the first version small and working.

Do not turn this into a giant Kingshot information system.

When deciding whether to add a field, ask:

> Will we realistically use this variable to interpret or compare battle experiments?

If no, leave it out until we have evidence we need it.

The experiment log should be optimized for practical use rather than completeness.
