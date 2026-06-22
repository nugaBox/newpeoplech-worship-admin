"""예배 목차 저장·조회 API."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/outlines", tags=["outlines"])

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "outlines.json"
FIELDS_FILE = Path(__file__).resolve().parent.parent / "data" / "mail_merge_fields.json"

# 목차 관리 화면에 표시할 필드
OUTLINE_FIELD_GROUPS = {
    "basic": {
        "label": "기본 정보",
        "fields": ["F_날짜", "F_주차", "F_호수", "F_광고1", "F_광고2", "F_광고3", "F_광고4", "F_광고5", "F_인용글_제목", "F_인용글_내용"],
    },
    "day": {
        "label": "주일낮예배",
        "fields": [
            "R_A_예배명", "R_A_경배찬송", "R_A_교독문번호", "R_A_교독문본문", "R_A_찬송1",
            "R_A_기도구분", "R_A_기도자", "R_A_본문", "R_A_본문페이지", "R_A_강해표시",
            "R_A_설교제목", "R_A_설교자", "R_A_봉헌찬송", "R_A_영광찬송", "R_A_차주기도",
        ],
    },
    "praise": {
        "label": "주일찬양예배",
        "fields": [
            "R_B_예배명", "R_B_인도설교", "R_B_인도자", "R_B_찬송", "R_B_기도자",
            "R_B_본문", "R_B_본문페이지", "R_B_강해표시", "R_B_설교제목", "R_B_차주기도",
        ],
    },
}


class OutlineFieldMeta(BaseModel):
    field: str
    label: str
    group: str
    sample: str = ""


class OutlineFieldsSchemaResponse(BaseModel):
    groups: dict[str, dict]
    fields: list[OutlineFieldMeta]


class OutlineRecord(BaseModel):
    id: str
    title: str
    date: str = ""
    updated_at: str
    fields: dict[str, str] = Field(default_factory=dict)


class OutlineListResponse(BaseModel):
    outlines: list[OutlineRecord]


class OutlineSaveRequest(BaseModel):
    id: str | None = None
    title: str = ""
    date: str = ""
    fields: dict[str, str]


def _load() -> dict:
    if not DATA_FILE.is_file():
        return {"outlines": []}
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _save(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _field_label(name: str) -> str:
    return name.split("_", 1)[-1] if "_" in name else name


@router.get("/schema", response_model=OutlineFieldsSchemaResponse)
async def outline_field_schema() -> OutlineFieldsSchemaResponse:
    samples: dict[str, str] = {}
    if FIELDS_FILE.is_file():
        for item in json.loads(FIELDS_FILE.read_text(encoding="utf-8")):
            samples[item["field"]] = item.get("sample", "") or ""

    fields: list[OutlineFieldMeta] = []
    for group_key, group in OUTLINE_FIELD_GROUPS.items():
        for field_name in group["fields"]:
            fields.append(
                OutlineFieldMeta(
                    field=field_name,
                    label=_field_label(field_name),
                    group=group["label"],
                    sample=samples.get(field_name, ""),
                )
            )
    return OutlineFieldsSchemaResponse(groups=OUTLINE_FIELD_GROUPS, fields=fields)


@router.get("", response_model=OutlineListResponse)
async def list_outlines() -> OutlineListResponse:
    data = _load()
    outlines = sorted(
        [OutlineRecord(**o) for o in data.get("outlines", [])],
        key=lambda o: o.updated_at,
        reverse=True,
    )
    return OutlineListResponse(outlines=outlines)


@router.get("/{outline_id}", response_model=OutlineRecord)
async def get_outline(outline_id: str) -> OutlineRecord:
    for item in _load().get("outlines", []):
        if item["id"] == outline_id:
            return OutlineRecord(**item)
    raise HTTPException(status_code=404, detail="목차를 찾을 수 없습니다.")


@router.post("", response_model=OutlineRecord)
async def save_outline(body: OutlineSaveRequest) -> OutlineRecord:
    data = _load()
    outlines = data.setdefault("outlines", [])
    now = datetime.now(timezone.utc).isoformat()
    title = body.title or body.date or body.fields.get("F_날짜", "새 목차")
    date = body.date or body.fields.get("F_날짜", "")

    if body.id:
        for item in outlines:
            if item["id"] == body.id:
                item["title"] = title
                item["date"] = date
                item["fields"] = body.fields
                item["updated_at"] = now
                _save(data)
                return OutlineRecord(**item)
        raise HTTPException(status_code=404, detail="목차를 찾을 수 없습니다.")

    record = {
        "id": uuid.uuid4().hex[:10],
        "title": title,
        "date": date,
        "updated_at": now,
        "fields": body.fields,
    }
    outlines.append(record)
    _save(data)
    return OutlineRecord(**record)


@router.delete("/{outline_id}")
async def delete_outline(outline_id: str) -> dict[str, str]:
    data = _load()
    outlines = data.get("outlines", [])
    new_list = [o for o in outlines if o["id"] != outline_id]
    if len(new_list) == len(outlines):
        raise HTTPException(status_code=404, detail="목차를 찾을 수 없습니다.")
    _save({"outlines": new_list})
    return {"message": "삭제되었습니다."}
