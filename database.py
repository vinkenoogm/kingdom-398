from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "battle_reports"
DB_PATH = DATA_DIR / "kingshot.db"


TURRET_BONUSES = {
    0: 0.00,
    1: 0.08,
    2: 0.12,
    3: 0.15,
    4: 0.20,
}


def ensure_app_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_app_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS player_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_code TEXT NOT NULL UNIQUE,
                player_name TEXT NOT NULL,
                snapshot_date TEXT NOT NULL,
                rally_capacity INTEGER,
                highest_troop_tier TEXT,
                infantry_attack REAL,
                infantry_defense REAL,
                infantry_lethality REAL,
                infantry_health REAL,
                cavalry_attack REAL,
                cavalry_defense REAL,
                cavalry_lethality REAL,
                cavalry_health REAL,
                archer_attack REAL,
                archer_defense REAL,
                archer_lethality REAL,
                archer_health REAL,
                infantry_hero TEXT,
                cavalry_hero TEXT,
                archer_hero TEXT,
                development_notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS formations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formation_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                purpose TEXT NOT NULL CHECK (purpose IN ('Attack', 'Defense')),
                infantry_hero TEXT,
                cavalry_hero TEXT,
                archer_hero TEXT,
                infantry_pct INTEGER NOT NULL,
                cavalry_pct INTEGER NOT NULL,
                archer_pct INTEGER NOT NULL,
                joiner_skill_1 TEXT,
                joiner_skill_2 TEXT,
                joiner_skill_3 TEXT,
                joiner_skill_4 TEXT,
                hypothesis TEXT,
                comparison_group TEXT,
                priority INTEGER NOT NULL DEFAULT 3,
                status TEXT NOT NULL DEFAULT 'Planned'
                    CHECK (status IN ('Planned', 'Testing', 'Promising', 'Proven', 'Dropped')),
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CHECK (infantry_pct + cavalry_pct + archer_pct = 100)
            );

            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_code TEXT NOT NULL UNIQUE,
                battle_datetime TEXT NOT NULL,
                player_snapshot_id INTEGER NOT NULL,
                formation_id INTEGER NOT NULL,
                battle_type TEXT NOT NULL CHECK (battle_type IN ('Controlled', 'Live KvK')),
                structure TEXT NOT NULL CHECK (structure IN ('Turret', 'Castle')),
                role TEXT NOT NULL CHECK (role IN ('Attack', 'Defense')),
                opponent TEXT,
                our_turret_count INTEGER NOT NULL DEFAULT 0 CHECK (our_turret_count BETWEEN 0 AND 4),
                enemy_turret_count INTEGER NOT NULL DEFAULT 0 CHECK (enemy_turret_count BETWEEN 0 AND 4),
                our_turret_bonus REAL NOT NULL DEFAULT 0,
                enemy_turret_bonus REAL NOT NULL DEFAULT 0,
                result TEXT NOT NULL CHECK (result IN ('Win', 'Loss')),
                our_casualties INTEGER,
                enemy_casualties INTEGER,
                kill_ratio REAL,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_snapshot_id) REFERENCES player_snapshots(id),
                FOREIGN KEY (formation_id) REFERENCES formations(id)
            );

            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                original_filename TEXT,
                uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_experiments_datetime
                ON experiments (battle_datetime);
            CREATE INDEX IF NOT EXISTS idx_experiments_snapshot
                ON experiments (player_snapshot_id);
            CREATE INDEX IF NOT EXISTS idx_experiments_formation
                ON experiments (formation_id);
            """
        )


def rows_for_table(table_name: str) -> list[sqlite3.Row]:
    allowed_tables = {
        "player_snapshots",
        "formations",
        "experiments",
        "screenshots",
    }
    if table_name not in allowed_tables:
        raise ValueError(f"Unsupported table: {table_name}")

    with get_connection() as conn:
        return list(conn.execute(f"SELECT * FROM {table_name} ORDER BY id DESC"))


def options_for(table_name: str, label_columns: Iterable[str]) -> dict[str, int]:
    rows = rows_for_table(table_name)
    options: dict[str, int] = {}
    for row in rows:
        label = " - ".join(str(row[col]) for col in label_columns if row[col])
        options[label or str(row["id"])] = row["id"]
    return options


def turret_bonus(turret_count: int) -> float:
    return TURRET_BONUSES.get(turret_count, 0.0)


def kill_ratio(enemy_casualties: int | None, our_casualties: int | None) -> float | None:
    if not enemy_casualties or not our_casualties:
        return None
    return enemy_casualties / our_casualties
