from pathlib import Path
import sqlite3
import streamlit as st

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "data.db"

@st.cache_resource
def get_connection() -> sqlite3.Connection:
    """Get a cached SQLite connection. Creates the data dir if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
        timeout=30,  # wait up to 30s if the DB is busy
    )
    conn.execute("PRAGMA foreign_keys = ON;")   # SQLite support for foreign keys is off by default
    conn.execute("PRAGMA journal_mode = WAL;")  # better for concurrent reads/writes
    return conn

def init_db() -> None:
    """Run schema.sql to create tables if they do not exist."""
    conn = get_connection()
    schema_path = Path(__file__).with_name("schema.sql")
    with schema_path.open(mode="r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()