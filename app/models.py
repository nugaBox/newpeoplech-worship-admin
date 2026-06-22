"""Pydantic 모델."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parent.parent
FIELDS_JSON = Path(__file__).resolve().parent / "data" / "mail_merge_fields.json"


def load_field_names() -> list[str]:
    if not FIELDS_JSON.is_file():
        return []
    data = json.loads(FIELDS_JSON.read_text(encoding="utf-8"))
    return [item["field"] for item in data]


FIELD_NAMES = load_field_names()


class BulletinFields(BaseModel):
    """메일머지 필드 입력 — xlsx 기준 65개 필드."""

    model_config = {"extra": "allow"}

    F_날짜: str = ""
    F_주차: str = ""
    F_호수: str = ""
    F_광고1: str = ""
    F_광고2: str = ""
    F_광고3: str = ""
    F_광고4: str = ""
    F_광고5: str = ""
    F_생일자: str = ""
    F_인용글_제목: str = ""
    F_인용글_내용: str = ""
    R_A_예배명: str = ""
    R_A_경배찬송: str = ""
    R_A_교독문번호: str = ""
    R_A_교독문본문: str = ""
    R_A_찬송1: str = ""
    R_A_기도구분: str = ""
    R_A_기도자: str = ""
    R_A_본문: str = ""
    R_A_본문페이지: str = ""
    R_A_강해표시: str = ""
    R_A_설교제목: str = ""
    R_A_설교자: str = ""
    R_A_봉헌찬송: str = ""
    R_A_영광찬송: str = ""
    R_A_차주기도: str = ""
    R_B_예배명: str = ""
    R_B_인도설교: str = ""
    R_B_인도자: str = ""
    R_B_찬송: str = ""
    R_B_기도자: str = ""
    R_B_차주기도: str = ""
    R_B_본문: str = ""
    R_B_본문페이지: str = ""
    R_B_강해표시: str = ""
    R_B_설교제목: str = ""
    R_C_예배명: str = ""
    R_C_인도설교: str = ""
    R_C_인도자: str = ""
    R_C_찬송: str = ""
    R_C_본문: str = ""
    R_C_본문페이지: str = ""
    R_C_강해표시: str = ""
    R_C_설교제목: str = ""
    R_문제호수: str = ""
    R_문제본문: str = ""
    R_문제1: str = ""
    R_문제2: str = ""
    R_문제3: str = ""
    R_문제4: str = ""
    R_문제5: str = ""
    R_문제6: str = ""
    R_문제7: str = ""
    R_문제8: str = ""
    R_문제9: str = ""
    R_문제10: str = ""
    R_묵상말씀: str = ""
    R_묵상본문: str = ""
    R_행사월: str = ""
    R_행사1주: str = ""
    R_행사2주: str = ""
    R_행사3주: str = ""
    R_행사4주: str = ""
    R_행사5주: str = ""
    R_행사5주_여부: str = ""

    def to_merge_dict(self) -> dict[str, str]:
        data = self.model_dump()
        return {k: (v if v is not None else "") for k, v in data.items()}


class GenerationResult(BaseModel):
    success: bool
    message: str
    filename: str = ""
    download_url: str = ""
    empty_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class FieldMeta(BaseModel):
    field: str
    sample: str = ""
    group: str = ""


class FieldsResponse(BaseModel):
    fields: list[FieldMeta]


def group_for_field(name: str) -> str:
    if name.startswith("F_"):
        return "기본 정보"
    if name.startswith("R_A_"):
        return "주일낮예배"
    if name.startswith("R_B_"):
        return "주일찬양예배"
    if name.startswith("R_C_"):
        return "주일찬양예배(2부)"
    if name.startswith("R_문제") or name in ("R_문제호수", "R_문제본문"):
        return "성경문제"
    if name.startswith("R_묵상"):
        return "묵상"
    if name.startswith("R_행사"):
        return "행사"
    return "기타"
