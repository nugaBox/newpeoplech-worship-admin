"""주보/PPT 생성 API."""

from __future__ import annotations

import json
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import settings
from app.models import BulletinFields, FieldMeta, FieldsResponse, GenerationResult, group_for_field

router = APIRouter(prefix="/api/bulletin", tags=["bulletin"])

FIELDS_JSON = Path(__file__).resolve().parent.parent / "data" / "mail_merge_fields.json"


def _require_windows_com() -> None:
    if sys.platform != "win32":
        raise HTTPException(
            status_code=503,
            detail="한글/PPT 생성은 Windows + 한글/PowerPoint 설치 환경에서만 동작합니다.",
        )


def _parse_fields_json(fields_json: str) -> dict[str, str]:
    try:
        data = json.loads(fields_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"fields JSON 파싱 오류: {exc}") from exc
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="fields는 JSON 객체여야 합니다.")
    return {str(k): str(v) if v is not None else "" for k, v in data.items()}


def _output_filename(prefix: str, ext: str, date_str: str) -> str:
    safe_date = date_str.replace(" ", "_").replace("년", "").replace("월", "").replace("일", "")
    safe_date = "".join(c for c in safe_date if c.isdigit() or c in "-_")
    if not safe_date:
        safe_date = datetime.now().strftime("%Y%m%d")
    return f"{prefix}_{safe_date}.{ext}"


async def _save_upload(upload: UploadFile | None, dest_dir: Path, key: str) -> Path | None:
    if upload is None or not upload.filename:
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename).suffix or ".pptx"
    dest = dest_dir / f"{key}_{uuid.uuid4().hex[:8]}{suffix}"
    with dest.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return dest


@router.get("/fields", response_model=FieldsResponse)
async def list_fields() -> FieldsResponse:
    if not FIELDS_JSON.is_file():
        raise HTTPException(status_code=500, detail="메일머지 필드 정의 파일이 없습니다.")
    raw = json.loads(FIELDS_JSON.read_text(encoding="utf-8"))
    fields = [
        FieldMeta(field=item["field"], sample=item.get("sample", ""), group=group_for_field(item["field"]))
        for item in raw
    ]
    return FieldsResponse(fields=fields)


@router.post("/hwp", response_model=GenerationResult)
async def create_hwp(fields_json: str = Form(...)) -> GenerationResult:
    _require_windows_com()
    fields = _parse_fields_json(fields_json)
    bulletin = BulletinFields(**fields)
    merge = bulletin.to_merge_dict()

    try:
        settings.validate_hwp_template()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    out_dir = settings.ensure_output_dir()
    filename = _output_filename("주보", "hwpx", merge.get("F_날짜", ""))
    output_path = out_dir / filename

    try:
        from app.engines.hwp_engine import generate_bulletin_hwp

        empty = generate_bulletin_hwp(settings.hwp_template_path, output_path, merge)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"주보 생성 실패: {exc}") from exc

    return GenerationResult(
        success=True,
        message="주보 생성이 완료되었습니다.",
        filename=filename,
        download_url=f"/api/bulletin/download/{filename}",
        empty_fields=empty,
        warnings=[f"빈 필드 {len(empty)}개"] if empty else [],
    )


@router.post("/ppt/day", response_model=GenerationResult)
async def create_day_ppt(
    fields_json: str = Form(...),
    sermon_file: UploadFile | None = File(None),
    ad_file: UploadFile | None = File(None),
    prayer_file: UploadFile | None = File(None),
) -> GenerationResult:
    _require_windows_com()
    fields = _parse_fields_json(fields_json)
    bulletin = BulletinFields(**fields)
    merge = bulletin.to_merge_dict()

    try:
        settings.validate_day_ppt_template()
        settings.validate_hymn_dir()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    out_dir = settings.ensure_output_dir()
    upload_dir = out_dir / "uploads"
    upload_paths: dict[str, Path] = {}

    if path := await _save_upload(prayer_file, upload_dir, "prayer"):
        upload_paths["대표기도파일"] = path
    if path := await _save_upload(sermon_file, upload_dir, "sermon"):
        upload_paths["설교파일"] = path
    if path := await _save_upload(ad_file, upload_dir, "ad"):
        upload_paths["광고파일"] = path

    filename = _output_filename("주일낮예배", "pptx", merge.get("F_날짜", ""))
    output_path = out_dir / filename

    try:
        from app.engines.ppt_engine import generate_day_ppt

        warnings = generate_day_ppt(
            template_path=settings.day_ppt_template_path,
            output_path=output_path,
            fields=merge,
            hymn_dir=settings.hymn_ppt_dir,
            responsive_dir=settings.responsive_ppt_dir,
            upload_paths=upload_paths,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"낮예배 PPT 생성 실패: {exc}") from exc

    return GenerationResult(
        success=True,
        message="주일낮예배 PPT 생성이 완료되었습니다.",
        filename=filename,
        download_url=f"/api/bulletin/download/{filename}",
        warnings=warnings,
    )


@router.get("/download/{filename}")
async def download_file(filename: str) -> FileResponse:
    safe_name = Path(filename).name
    file_path = settings.output_dir / safe_name
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {safe_name}")
    return FileResponse(
        path=file_path,
        filename=safe_name,
        media_type="application/octet-stream",
    )
