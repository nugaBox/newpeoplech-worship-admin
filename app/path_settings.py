"""템플릿·작업 폴더 경로 — SQLite 저장."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent / "data"
DB_FILE = DATA_DIR / "worship.db"

PathKind = Literal["file", "dir"]
PathGroup = Literal["document", "quick_start"]

PATH_GROUP_LABELS: dict[PathGroup, str] = {
    "document": "문서·생성",
    "quick_start": "빠른 시작",
}


class PathDefinition(TypedDict):
    label: str
    kind: PathKind
    default: str
    env_key: str
    group: PathGroup
    hint: str


PATH_DEFINITIONS: dict[str, PathDefinition] = {
    "hwp_template": {
        "label": "주보 hwpx 템플릿",
        "kind": "file",
        "default": r"C:\Users\churchCom\Documents\churchCloud\교회 문서\03 주보\광주새백성교회_주보_2026_메일머지.hwpx",
        "env_key": "HWP_TEMPLATE_PATH",
        "group": "document",
        "hint": "",
    },
    "day_ppt_template": {
        "label": "주일낮예배 PPT 템플릿",
        "kind": "file",
        "default": r"C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\주일낮예배-2026-템플릿.pptx",
        "env_key": "DAY_PPT_TEMPLATE_PATH",
        "group": "document",
        "hint": "",
    },
    "hymn_ppt_dir": {
        "label": "찬송가 PPT 폴더",
        "kind": "dir",
        "default": r"C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\찬송가 PPT",
        "env_key": "HYMN_PPT_DIR",
        "group": "document",
        "hint": "주일낮예배 PPT 생성 시 사용",
    },
    "responsive_ppt_dir": {
        "label": "교독문 PPT 폴더",
        "kind": "dir",
        "default": r"C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\교독문 PPT",
        "env_key": "RESPONSIVE_PPT_DIR",
        "group": "document",
        "hint": "주일낮예배 PPT 생성 시 사용",
    },
    "output_dir": {
        "label": "생성 파일 출력 폴더",
        "kind": "dir",
        "default": str(ROOT_DIR / "app" / "data" / "output"),
        "env_key": "OUTPUT_DIR",
        "group": "document",
        "hint": "",
    },
    "hymn_slideshow_dir": {
        "label": "찬송가 슬라이드쇼 폴더",
        "kind": "dir",
        "default": r"C:\Users\churchCom\Documents\churchCloud\찬양 자료\찬송가 PPT",
        "env_key": "HYMN_SLIDESHOW_DIR",
        "group": "quick_start",
        "hint": "홈 빠른 시작 · 찬001_…ppsx (1~645장)",
    },
    "responsive_slideshow_dir": {
        "label": "교독문 슬라이드쇼 폴더",
        "kind": "dir",
        "default": r"C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\교독문 PPT",
        "env_key": "RESPONSIVE_SLIDESHOW_DIR",
        "group": "quick_start",
        "hint": "홈 빠른 시작 · 교독문001_…ppsx",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _seed_value(key: str) -> str:
    defn = PATH_DEFINITIONS[key]
    env_val = os.getenv(defn["env_key"], "").strip()
    if env_val:
        path = Path(env_val)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return str(path)
    return defn["default"]


def init_path_db() -> None:
    """DB 테이블 생성 및 누락된 경로 키 시드."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS path_settings (
                key TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        for key in PATH_DEFINITIONS:
            row = conn.execute(
                "SELECT 1 FROM path_settings WHERE key = ?",
                (key,),
            ).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO path_settings (key, path, updated_at) VALUES (?, ?, ?)",
                    (key, _seed_value(key), _now()),
                )
        conn.commit()


def get_stored_path(key: str) -> str | None:
    if key not in PATH_DEFINITIONS:
        raise KeyError(f"알 수 없는 경로 키입니다: {key}")
    with _connect() as conn:
        row = conn.execute(
            "SELECT path FROM path_settings WHERE key = ?",
            (key,),
        ).fetchone()
    return str(row["path"]) if row else None


def get_resolved_path(key: str) -> Path:
    stored = get_stored_path(key)
    if stored:
        path = Path(stored)
        if key == "output_dir" and not path.is_absolute():
            return ROOT_DIR / path
        return path
    return Path(_seed_value(key))


def set_path(key: str, path: str) -> None:
    if key not in PATH_DEFINITIONS:
        raise KeyError(f"알 수 없는 경로 키입니다: {key}")
    cleaned = path.strip()
    if not cleaned:
        raise ValueError("경로가 비어 있습니다.")
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO path_settings (key, path, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                path = excluded.path,
                updated_at = excluded.updated_at
            """,
            (key, cleaned, _now()),
        )
        conn.commit()


def path_exists(key: str, path: Path) -> bool:
    kind = PATH_DEFINITIONS[key]["kind"]
    return path.is_file() if kind == "file" else path.is_dir()


def list_path_checks() -> list[dict[str, str | bool]]:
    rows: list[dict[str, str | bool]] = []
    for key, defn in PATH_DEFINITIONS.items():
        path = get_resolved_path(key)
        group = defn["group"]
        rows.append(
            {
                "key": key,
                "label": defn["label"],
                "path": str(path),
                "exists": path_exists(key, path),
                "kind": defn["kind"],
                "group": group,
                "group_label": PATH_GROUP_LABELS[group],
                "hint": defn.get("hint", ""),
            }
        )
    return rows
