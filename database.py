from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    func,
    insert,
    select,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "battle_reports"
DB_PATH = DATA_DIR / "kingshot.db"
DATABASE_URL = os.getenv("DATABASE_URL")


TURRET_BONUSES = {
    0: 0.00,
    1: 0.08,
    2: 0.12,
    3: 0.15,
    4: 0.20,
}

metadata = MetaData()

player_snapshots = Table(
    "player_snapshots",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("snapshot_code", String, nullable=False, unique=True),
    Column("player_name", String, nullable=False),
    Column("snapshot_date", String, nullable=False),
    Column("rally_capacity", Integer),
    Column("highest_troop_tier", String),
    Column("infantry_troop_tier", String),
    Column("infantry_truegold_level", String),
    Column("cavalry_troop_tier", String),
    Column("cavalry_truegold_level", String),
    Column("archer_troop_tier", String),
    Column("archer_truegold_level", String),
    Column("development_notes", Text),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("updated_at", DateTime, nullable=False, server_default=func.now()),
)

snapshot_heroes = Table(
    "snapshot_heroes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("player_snapshot_id", Integer, ForeignKey("player_snapshots.id", ondelete="CASCADE"), nullable=False),
    Column("hero_name", String, nullable=False),
    Column("troop_type", String, nullable=False),
    Column("star_level", Float),
    Column("widget_level", Integer),
    Column("notes", Text),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    CheckConstraint("troop_type IN ('Infantry', 'Cavalry', 'Archers')"),
)

formations = Table(
    "formations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("formation_code", String, nullable=False, unique=True),
    Column("name", String, nullable=False),
    Column("purpose", String, nullable=False),
    Column("infantry_hero", String),
    Column("cavalry_hero", String),
    Column("archer_hero", String),
    Column("infantry_pct", Integer, nullable=False),
    Column("cavalry_pct", Integer, nullable=False),
    Column("archer_pct", Integer, nullable=False),
    Column("joiner_skill_1", String),
    Column("joiner_skill_2", String),
    Column("joiner_skill_3", String),
    Column("joiner_skill_4", String),
    Column("hypothesis", Text),
    Column("comparison_group", String),
    Column("priority", Integer, nullable=False, server_default="3"),
    Column("status", String, nullable=False, server_default="Planned"),
    Column("notes", Text),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("updated_at", DateTime, nullable=False, server_default=func.now()),
    CheckConstraint("purpose IN ('Attack', 'Defense')"),
    CheckConstraint("status IN ('Planned', 'Testing', 'Promising', 'Proven', 'Dropped')"),
    CheckConstraint("infantry_pct + cavalry_pct + archer_pct = 100"),
)

experiments = Table(
    "experiments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("experiment_code", String, nullable=False, unique=True),
    Column("battle_datetime", String, nullable=False),
    Column("player_snapshot_id", Integer, ForeignKey("player_snapshots.id"), nullable=False),
    Column("formation_id", Integer, ForeignKey("formations.id"), nullable=False),
    Column("enemy_player_snapshot_id", Integer, ForeignKey("player_snapshots.id")),
    Column("enemy_formation_id", Integer, ForeignKey("formations.id")),
    Column("opponent_source", String, nullable=False, server_default="New / from report"),
    Column("battle_type", String, nullable=False),
    Column("structure", String, nullable=False),
    Column("role", String, nullable=False),
    Column("opponent", String),
    Column("opponent_formation_summary", Text),
    Column("our_total_troops", Integer),
    Column("enemy_total_troops", Integer),
    Column("our_remaining_troops", Integer),
    Column("enemy_remaining_troops", Integer),
    Column("our_turret_count", Integer, nullable=False, server_default="0"),
    Column("enemy_turret_count", Integer, nullable=False, server_default="0"),
    Column("our_turret_bonus", Float, nullable=False, server_default="0"),
    Column("enemy_turret_bonus", Float, nullable=False, server_default="0"),
    Column("result", String, nullable=False),
    Column("our_casualties", Integer),
    Column("enemy_casualties", Integer),
    Column("kill_ratio", Float),
    Column("report_infantry_attack", Float),
    Column("report_infantry_defense", Float),
    Column("report_infantry_lethality", Float),
    Column("report_infantry_health", Float),
    Column("report_cavalry_attack", Float),
    Column("report_cavalry_defense", Float),
    Column("report_cavalry_lethality", Float),
    Column("report_cavalry_health", Float),
    Column("report_archer_attack", Float),
    Column("report_archer_defense", Float),
    Column("report_archer_lethality", Float),
    Column("report_archer_health", Float),
    Column("enemy_report_infantry_attack", Float),
    Column("enemy_report_infantry_defense", Float),
    Column("enemy_report_infantry_lethality", Float),
    Column("enemy_report_infantry_health", Float),
    Column("enemy_report_cavalry_attack", Float),
    Column("enemy_report_cavalry_defense", Float),
    Column("enemy_report_cavalry_lethality", Float),
    Column("enemy_report_cavalry_health", Float),
    Column("enemy_report_archer_attack", Float),
    Column("enemy_report_archer_defense", Float),
    Column("enemy_report_archer_lethality", Float),
    Column("enemy_report_archer_health", Float),
    Column("notes", Text),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("updated_at", DateTime, nullable=False, server_default=func.now()),
    CheckConstraint("battle_type IN ('Controlled', 'Live KvK')"),
    CheckConstraint("structure IN ('Castle', 'Non-castle')"),
    CheckConstraint("role IN ('Attack', 'Defense')"),
    CheckConstraint("result IN ('Win', 'Loss')"),
    CheckConstraint("our_turret_count BETWEEN 0 AND 4"),
    CheckConstraint("enemy_turret_count BETWEEN 0 AND 4"),
)

screenshots = Table(
    "screenshots",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("experiment_id", Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False),
    Column("file_path", Text, nullable=False),
    Column("original_filename", String),
    Column("uploaded_at", DateTime, nullable=False, server_default=func.now()),
)

TABLES = {
    "player_snapshots": player_snapshots,
    "snapshot_heroes": snapshot_heroes,
    "formations": formations,
    "experiments": experiments,
    "screenshots": screenshots,
}

_engine: Engine | None = None


def ensure_app_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)


def database_url() -> str:
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            return DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return DATABASE_URL
    ensure_app_dirs()
    return f"sqlite:///{DB_PATH}"


def database_label() -> str:
    return "Neon Postgres" if DATABASE_URL else str(DB_PATH.relative_to(BASE_DIR))


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        connect_args = {}
        if DATABASE_URL and "sslmode=" not in DATABASE_URL:
            connect_args["sslmode"] = "require"
        _engine = create_engine(database_url(), connect_args=connect_args, pool_pre_ping=True)
    return _engine


def init_db() -> None:
    metadata.create_all(get_engine())


def rows_for_table(table_name: str) -> list[dict]:
    table = TABLES.get(table_name)
    if table is None:
        raise ValueError(f"Unsupported table: {table_name}")

    with get_engine().connect() as conn:
        rows = conn.execute(select(table).order_by(table.c.id.desc())).mappings().all()
        return [dict(row) for row in rows]


def insert_row(table: Table, values: dict[str, object]) -> int:
    filtered_values = {
        key: value for key, value in values.items() if key in table.c
    }
    with get_engine().begin() as conn:
        result = conn.execute(insert(table), filtered_values)
        inserted_id = result.inserted_primary_key[0]
        if inserted_id is None:
            inserted_id = conn.execute(select(func.max(table.c.id))).scalar_one()
        return int(inserted_id)


def create_player_snapshot(values: dict[str, object]) -> int:
    return insert_row(player_snapshots, values)


def create_snapshot_heroes(
    player_snapshot_id: int, hero_rows: Iterable[dict[str, object]]
) -> int:
    clean_rows = [
        {
            "player_snapshot_id": player_snapshot_id,
            "hero_name": str(row.get("hero_name", "")).strip(),
            "troop_type": row.get("troop_type"),
            "star_level": row.get("star_level"),
            "widget_level": row.get("widget_level"),
            "notes": str(row.get("notes", "")).strip(),
        }
        for row in hero_rows
        if str(row.get("hero_name", "")).strip()
    ]
    if not clean_rows:
        return 0

    with get_engine().begin() as conn:
        conn.execute(insert(snapshot_heroes), clean_rows)
    return len(clean_rows)


def create_formation(values: dict[str, object]) -> int:
    return insert_row(formations, values)


def next_experiment_code() -> str:
    with get_engine().connect() as conn:
        last_code = conn.execute(
            select(experiments.c.experiment_code)
            .where(experiments.c.experiment_code.like("EXP-%"))
            .order_by(experiments.c.id.desc())
            .limit(1)
        ).scalar_one_or_none()

    if not last_code:
        return "EXP-0001"
    try:
        last_number = int(str(last_code).split("-")[-1])
    except ValueError:
        last_number = 0
    return f"EXP-{last_number + 1:04d}"


def create_experiment(values: dict[str, object]) -> tuple[int, str]:
    experiment_code = next_experiment_code()
    experiment_id = insert_row(
        experiments,
        {**values, "experiment_code": experiment_code},
    )
    return experiment_id, experiment_code


def create_screenshot_record(
    experiment_id: int, file_path: Path | str, original_filename: str
) -> int:
    return insert_row(
        screenshots,
        {
            "experiment_id": experiment_id,
            "file_path": str(file_path),
            "original_filename": original_filename,
        },
    )


def heroes_for_snapshot(snapshot_id: int) -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            select(snapshot_heroes)
            .where(snapshot_heroes.c.player_snapshot_id == snapshot_id)
            .order_by(snapshot_heroes.c.troop_type, snapshot_heroes.c.hero_name)
        ).mappings().all()
        return [dict(row) for row in rows]


def seed_default_formations() -> int:
    defaults = [
        {
            "formation_code": "ATK-01",
            "name": "Charles / Ava / Wee & Woo - 50/20/30",
            "purpose": "Attack",
            "infantry_hero": "Charles",
            "cavalry_hero": "Ava",
            "archer_hero": "Wee & Woo",
            "infantry_pct": 50,
            "cavalry_pct": 20,
            "archer_pct": 30,
            "joiner_skill_1": "",
            "joiner_skill_2": "",
            "joiner_skill_3": "",
            "joiner_skill_4": "",
            "hypothesis": "Baseline Gen 7 attack ratio candidate.",
            "comparison_group": "Troop ratio test A",
            "priority": 1,
            "status": "Planned",
            "notes": "",
        },
        {
            "formation_code": "ATK-02",
            "name": "Charles / Ava / Wee & Woo - 50/10/40",
            "purpose": "Attack",
            "infantry_hero": "Charles",
            "cavalry_hero": "Ava",
            "archer_hero": "Wee & Woo",
            "infantry_pct": 50,
            "cavalry_pct": 10,
            "archer_pct": 40,
            "joiner_skill_1": "",
            "joiner_skill_2": "",
            "joiner_skill_3": "",
            "joiner_skill_4": "",
            "hypothesis": "Tests whether shifting troop share from cavalry to archers improves outcomes.",
            "comparison_group": "Troop ratio test A",
            "priority": 1,
            "status": "Planned",
            "notes": "",
        },
        {
            "formation_code": "ATK-03",
            "name": "Charles / Ava / Wee & Woo - 48/4/48",
            "purpose": "Attack",
            "infantry_hero": "Charles",
            "cavalry_hero": "Ava",
            "archer_hero": "Wee & Woo",
            "infantry_pct": 48,
            "cavalry_pct": 4,
            "archer_pct": 48,
            "joiner_skill_1": "",
            "joiner_skill_2": "",
            "joiner_skill_3": "",
            "joiner_skill_4": "",
            "hypothesis": "Tests a very low cavalry, high archer setup.",
            "comparison_group": "Troop ratio test A",
            "priority": 2,
            "status": "Planned",
            "notes": "",
        },
        {
            "formation_code": "ATK-04",
            "name": "Charles / Ava / Wee & Woo - 50/0/50",
            "purpose": "Attack",
            "infantry_hero": "Charles",
            "cavalry_hero": "Ava",
            "archer_hero": "Wee & Woo",
            "infantry_pct": 50,
            "cavalry_pct": 0,
            "archer_pct": 50,
            "joiner_skill_1": "",
            "joiner_skill_2": "",
            "joiner_skill_3": "",
            "joiner_skill_4": "",
            "hypothesis": "Tests whether dropping cavalry entirely is useful in controlled fights.",
            "comparison_group": "Troop ratio test A",
            "priority": 2,
            "status": "Planned",
            "notes": "",
        },
    ]

    inserted = 0
    for formation in defaults:
        try:
            create_formation(formation)
            inserted += 1
        except IntegrityError:
            continue
    return inserted


def options_for(table_name: str, label_columns: Iterable[str]) -> dict[str, int]:
    rows = rows_for_table(table_name)
    options: dict[str, int] = {}
    for row in rows:
        label = " - ".join(str(row[col]) for col in label_columns if row.get(col))
        options[label or str(row["id"])] = row["id"]
    return options


def turret_bonus(turret_count: int) -> float:
    return TURRET_BONUSES.get(turret_count, 0.0)


def kill_ratio(enemy_casualties: int | None, our_casualties: int | None) -> float | None:
    if not enemy_casualties or not our_casualties:
        return None
    return enemy_casualties / our_casualties
