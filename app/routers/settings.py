"""설정 API — 경로 검증, 개발/운영 모드."""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.engines.folder_picker import pick_path
from app.path_settings import (
    PATH_DEFINITIONS,
    PATH_GROUP_LABELS,
    get_resolved_path,
    list_path_checks,
    path_exists,
    set_path,
)
from app.runtime_settings import (
    RunMode,
    RuntimeSettings,
    load_runtime_settings,
    save_runtime_settings,
)

router = APIRouter(prefix="/api/settings", tags=["settings"])


class PathCheck(BaseModel):
    key: str
    label: str
    path: str
    exists: bool
    kind: str
    group: str = "document"
    group_label: str = ""
    hint: str = ""


class PathsResponse(BaseModel):
    paths: list[PathCheck]


class PathUpdate(BaseModel):
    path: str


class RuntimeSettingsResponse(BaseModel):
    run_mode: RunMode
    mode_label: str
    host: str
    port: int
    open_browser: bool
    reload_enabled: bool


class RuntimeSettingsUpdate(BaseModel):
    run_mode: RunMode
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1024, le=65535)
    open_browser: bool = False


def _to_path_check(row: dict[str, str | bool]) -> PathCheck:
    return PathCheck(
        key=str(row["key"]),
        label=str(row["label"]),
        path=str(row["path"]),
        exists=bool(row["exists"]),
        kind=str(row["kind"]),
        group=str(row.get("group", "document")),
        group_label=str(row.get("group_label", "")),
        hint=str(row.get("hint", "")),
    )


def _initial_dir_for_key(key: str) -> str | None:
    current = get_resolved_path(key)
    kind = PATH_DEFINITIONS[key]["kind"]
    if kind == "file":
        if current.is_file():
            return str(current.parent)
        if current.parent.is_dir():
            return str(current.parent)
        return None
    if current.is_dir():
        return str(current)
    if current.parent.is_dir():
        return str(current.parent)
    return None


@router.get("/paths", response_model=PathsResponse)
async def check_paths() -> PathsResponse:
    return PathsResponse(paths=[_to_path_check(row) for row in list_path_checks()])


def _path_check_from_key(key: str, path: Path) -> PathCheck:
    defn = PATH_DEFINITIONS[key]
    group = defn["group"]
    return PathCheck(
        key=key,
        label=defn["label"],
        path=str(path),
        exists=path_exists(key, path),
        kind=defn["kind"],
        group=group,
        group_label=PATH_GROUP_LABELS[group],
        hint=defn.get("hint", ""),
    )


@router.put("/paths/{key}", response_model=PathCheck)
async def update_path(key: str, body: PathUpdate) -> PathCheck:
    if key not in PATH_DEFINITIONS:
        raise HTTPException(status_code=404, detail="경로 항목을 찾을 수 없습니다.")
    try:
        set_path(key, body.path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _path_check_from_key(key, get_resolved_path(key))


@router.post("/paths/{key}/browse", response_model=PathCheck)
async def browse_path(key: str) -> PathCheck:
    if key not in PATH_DEFINITIONS:
        raise HTTPException(status_code=404, detail="경로 항목을 찾을 수 없습니다.")

    defn = PATH_DEFINITIONS[key]
    try:
        picked = await asyncio.to_thread(
            pick_path,
            kind=defn["kind"],
            initial_dir=_initial_dir_for_key(key),
        )
    except OSError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not picked:
        raise HTTPException(status_code=400, detail="선택이 취소되었습니다.")

    set_path(key, picked)
    return _path_check_from_key(key, Path(picked))


@router.get("/runtime", response_model=RuntimeSettingsResponse)
async def get_runtime_settings() -> RuntimeSettingsResponse:
    rt = load_runtime_settings()
    return RuntimeSettingsResponse(
        run_mode=rt.run_mode,
        mode_label=rt.mode_label,
        host=rt.host,
        port=rt.port,
        open_browser=rt.open_browser,
        reload_enabled=rt.is_development,
    )


@router.post("/runtime", response_model=RuntimeSettingsResponse)
async def update_runtime_settings(body: RuntimeSettingsUpdate) -> RuntimeSettingsResponse:
    updated = RuntimeSettings(
        run_mode=body.run_mode,
        host=body.host,
        port=body.port,
        open_browser=body.open_browser,
    )
    save_runtime_settings(updated)
    return RuntimeSettingsResponse(
        run_mode=updated.run_mode,
        mode_label=updated.mode_label,
        host=updated.host,
        port=updated.port,
        open_browser=updated.open_browser,
        reload_enabled=updated.is_development,
    )
