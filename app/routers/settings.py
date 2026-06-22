"""설정 API — 경로 검증, 개발/운영 모드."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import settings
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


class PathsResponse(BaseModel):
    paths: list[PathCheck]


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


@router.get("/paths", response_model=PathsResponse)
async def check_paths() -> PathsResponse:
    checks = [
        ("hwp_template", "주보 hwpx 템플릿", settings.hwp_template_path, "file"),
        ("day_ppt_template", "주일낮예배 PPT 템플릿", settings.day_ppt_template_path, "file"),
        ("hymn_ppt_dir", "찬송가 PPT 폴더", settings.hymn_ppt_dir, "dir"),
        ("responsive_ppt_dir", "교독문 PPT 폴더", settings.responsive_ppt_dir, "dir"),
        ("output_dir", "생성 파일 출력 폴더", settings.ensure_output_dir(), "dir"),
    ]
    paths: list[PathCheck] = []
    for key, label, path, kind in checks:
        exists = path.is_file() if kind == "file" else path.is_dir()
        paths.append(
            PathCheck(
                key=key,
                label=label,
                path=str(path),
                exists=exists,
                kind=kind,
            )
        )
    return PathsResponse(paths=paths)


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

