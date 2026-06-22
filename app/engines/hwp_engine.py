"""한글(HWP) COM 제어 — 주보 메일머지 생성."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_hwp():
    import win32com.client as win32

    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
    try:
        hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    except Exception:
        pass
    return hwp


def _format_hwp_value(value: str) -> str:
    """한글 줄바꿈: ^ → \\n (엔터)."""
    return (value or "").replace("^", "\n")


def generate_bulletin_hwp(
    template_path: Path,
    output_path: Path,
    fields: dict[str, str],
) -> list[str]:
    """
    hwpx 템플릿에 메일머지 필드를 치환해 저장한다.
    빈 필드명 목록을 반환한다.
    """
    empty_fields: list[str] = []
    hwp = None
    try:
        hwp = _get_hwp()
        try:
            hwp.XHwpWindows.Item(0).Visible = False
        except Exception:
            pass

        if not hwp.Open(str(template_path)):
            raise RuntimeError(f"한글 템플릿을 열 수 없습니다: {template_path}")

        for field_name, raw_value in fields.items():
            value = _format_hwp_value(raw_value)
            if not value.strip():
                empty_fields.append(field_name)

            replaced = False
            try:
                hwp.PutFieldText(field_name, value)
                replaced = True
            except Exception:
                logger.debug("PutFieldText 실패, AllReplace 시도: %s", field_name)

            if not replaced:
                try:
                    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
                    opts = hwp.HParameterSet.HFindReplace
                    opts.FindString = f"{{{{{field_name}}}}}"
                    opts.ReplaceString = value
                    opts.IgnoreMessage = 1
                    hwp.HAction.Execute("AllReplace", opts.HSet)
                except Exception as exc:
                    logger.warning("필드 치환 실패 (%s): %s", field_name, exc)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            output_path.unlink()
        hwp.SaveAs(str(output_path.resolve()), "HWPX")
        if not output_path.is_file():
            raise RuntimeError(f"주보 파일 저장에 실패했습니다: {output_path}")
    finally:
        if hwp is not None:
            try:
                hwp.Clear(1)
                hwp.Quit()
            except Exception:
                pass

    return empty_fields
