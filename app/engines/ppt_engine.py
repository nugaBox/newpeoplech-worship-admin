"""PowerPoint COM 제어 — 주일낮예배 PPT 생성."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from app.engines.file_matcher import FileMatchError, find_hymn_file, find_responsive_file

logger = logging.getLogger(__name__)

SECTION_CONFIG_PATH = Path(__file__).resolve().parent.parent / "section_config" / "sunday_day.json"


def _get_powerpoint():
    import win32com.client as win32

    return win32.gencache.EnsureDispatch("PowerPoint.Application")


def load_section_config() -> dict[str, Any]:
    return json.loads(SECTION_CONFIG_PATH.read_text(encoding="utf-8"))


def _slide_text(slide) -> str:
    parts: list[str] = []
    for shape in slide.Shapes:
        if shape.HasTextFrame:
            try:
                parts.append(shape.TextFrame.TextRange.Text)
            except Exception:
                continue
    return "".join(parts)


def _find_marker_slide_index(presentation, marker: str) -> int | None:
    for i in range(1, presentation.Slides.Count + 1):
        if marker in _slide_text(presentation.Slides(i)):
            return i
    return None


def _replace_placeholders(presentation, placeholders: dict[str, str], fields: dict[str, str]) -> None:
    for ph, field_key in placeholders.items():
        value = fields.get(field_key, "")
        for i in range(1, presentation.Slides.Count + 1):
            slide = presentation.Slides(i)
            for shape in slide.Shapes:
                if not shape.HasTextFrame:
                    continue
                try:
                    text_range = shape.TextFrame.TextRange
                    if ph in text_range.Text:
                        text_range.Text = text_range.Text.replace(ph, value)
                except Exception:
                    continue


def _insert_slides_from_file(presentation, index: int, source_path: Path) -> None:
    """마커 슬라이드 위치에 source_path의 모든 슬라이드를 삽입."""
    presentation.Slides.InsertFromFile(str(source_path), index, 1, -1)


def _delete_slide(presentation, index: int) -> None:
    presentation.Slides(index).Delete()


def _resolve_section_source(
    section: dict[str, Any],
    fields: dict[str, str],
    upload_paths: dict[str, Path],
    hymn_dir: Path,
    responsive_dir: Path,
) -> Path | None:
    section_type = section["type"]
    field_key = section["field"]

    if section_type == "hymn_lib":
        return find_hymn_file(hymn_dir, fields.get(field_key, ""))
    if section_type == "responsive_lib":
        return find_responsive_file(responsive_dir, fields.get(field_key, ""))
    if section_type == "upload":
        return upload_paths.get(field_key)
    if section_type == "scripture":
        return None
    raise ValueError(f"알 수 없는 구역 타입: {section_type}")


def generate_day_ppt(
    template_path: Path,
    output_path: Path,
    fields: dict[str, str],
    hymn_dir: Path,
    responsive_dir: Path,
    upload_paths: dict[str, Path] | None = None,
) -> list[str]:
    """
    주일낮예배 PPT를 생성한다.
    경고/안내 메시지 목록을 반환한다.
    """
    warnings: list[str] = []
    config = load_section_config()
    uploads = upload_paths or {}
    ppt = None
    presentation = None

    try:
        ppt = _get_powerpoint()
        ppt.Visible = True
        presentation = ppt.Presentations.Open(str(template_path), WithWindow=False)

        placeholders = config.get("placeholders", {})
        _replace_placeholders(presentation, placeholders, fields)

        for section in config.get("sections", []):
            marker = section["marker"]
            section_type = section["type"]
            field_key = section["field"]
            marker_index = _find_marker_slide_index(presentation, marker)

            if marker_index is None:
                if section_type == "scripture":
                    continue
                warnings.append(
                    f"템플릿에서 마커 '{marker}' 슬라이드를 찾지 못했습니다. "
                    f"({field_key} 구역 건너뜀)"
                )
                continue

            if section_type == "scripture":
                _delete_slide(presentation, marker_index)
                continue

            try:
                source = _resolve_section_source(
                    section, fields, uploads, hymn_dir, responsive_dir
                )
            except FileMatchError as exc:
                warnings.append(str(exc))
                if exc.candidates:
                    warnings.append("후보: " + ", ".join(exc.candidates))
                continue

            if source is None or not source.is_file():
                warnings.append(
                    f"'{field_key}' 구역에 사용할 파일이 없습니다. "
                    f"({section_type})"
                )
                continue

            _insert_slides_from_file(presentation, marker_index, source)
            new_marker_index = _find_marker_slide_index(presentation, marker)
            if new_marker_index is not None:
                _delete_slide(presentation, new_marker_index)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        presentation.SaveAs(str(output_path.resolve()))
        if not output_path.is_file():
            raise RuntimeError(f"PPT 파일 저장에 실패했습니다: {output_path}")
    finally:
        if presentation is not None:
            try:
                presentation.Close()
            except Exception:
                pass
        if ppt is not None:
            try:
                ppt.Quit()
            except Exception:
                pass

    return warnings


def extract_number_from_field(value: str) -> str | None:
    match = re.search(r"(\d+)", value or "")
    return match.group(1) if match else None
