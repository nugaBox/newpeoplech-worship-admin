"""홈 빠른 시작 — 찬송가·교독문 슬라이드쇼 실행."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.engines.file_matcher import FileMatchError, find_hymn_slideshow_file, find_responsive_slideshow_file
from app.engines.local_runner import open_path
from app.path_settings import get_resolved_path

router = APIRouter(prefix="/api/quick-start", tags=["quick-start"])

NOT_FOUND_MESSAGE = "해당 파일이 없습니다."


class HymnRunRequest(BaseModel):
    number: int = Field(ge=1, le=645, description="찬송가 장 번호 (1~645)")


class NumberRunRequest(BaseModel):
    number: int = Field(ge=1, le=999, description="장 번호")


class ActionResult(BaseModel):
    success: bool
    message: str
    file_name: str = ""


def _raise_match_error(exc: FileMatchError) -> None:
    if not exc.candidates:
        raise HTTPException(status_code=404, detail=NOT_FOUND_MESSAGE) from exc
    detail = str(exc)
    if exc.candidates:
        detail += " 후보: " + ", ".join(exc.candidates)
    raise HTTPException(status_code=400, detail=detail) from exc


def _run_slideshow(
  *,
    directory: Path,
    number: int,
    find_file: Callable[[Path, str], Path],
    success_label: str,
) -> ActionResult:
    if not directory.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"폴더를 찾을 수 없습니다: {directory}",
        )
    try:
        target = find_file(directory, str(number))
        open_path(target)
    except FileMatchError as exc:
        _raise_match_error(exc)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=NOT_FOUND_MESSAGE) from exc
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"실행 실패: {exc}") from exc

    return ActionResult(
        success=True,
        message=f"{number}장 {success_label}을(를) 실행했습니다.",
        file_name=target.name,
    )


@router.post("/hymn", response_model=ActionResult)
async def run_hymn_slideshow(body: HymnRunRequest) -> ActionResult:
    return _run_slideshow(
        directory=get_resolved_path("hymn_slideshow_dir"),
        number=body.number,
        find_file=find_hymn_slideshow_file,
        success_label="슬라이드쇼",
    )


@router.post("/responsive", response_model=ActionResult)
async def run_responsive_slideshow(body: NumberRunRequest) -> ActionResult:
    return _run_slideshow(
        directory=get_resolved_path("responsive_slideshow_dir"),
        number=body.number,
        find_file=find_responsive_slideshow_file,
        success_label="교독문 슬라이드쇼",
    )
