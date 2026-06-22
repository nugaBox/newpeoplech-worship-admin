"""SQLite 연결 및 인증 스키마 초기화 (worship.db 공용)."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from app.path_settings import DATA_DIR, DB_FILE

_SCHEMA = """
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    remember INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db(admin_username: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(_SCHEMA)
        row = conn.execute(
            "SELECT id FROM admin WHERE username = ?",
            (admin_username,),
        ).fetchone()
        if row is None:
            now = _utc_now()
            conn.execute(
                """
                INSERT INTO admin (username, password_hash, created_at, updated_at)
                VALUES (?, NULL, ?, ?)
                """,
                (admin_username, now, now),
            )


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def db_path() -> Path:
    return DB_FILE
