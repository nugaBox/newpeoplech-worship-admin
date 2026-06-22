"""찬송가·교독문 파일명 매칭."""

import re
from pathlib import Path


class FileMatchError(Exception):
    """파일 매칭 실패."""

    def __init__(self, message: str, candidates: list[str] | None = None):
        super().__init__(message)
        self.candidates = candidates or []


def extract_number(value: str) -> str:
    """'35장', '337장', '35번' 등에서 숫자만 추출."""
    match = re.search(r"(\d+)", value or "")
    if not match:
        raise FileMatchError(f"번호를 추출할 수 없습니다: '{value}'")
    return match.group(1)


def pad_number(number: str | int) -> str:
    """숫자를 3자리 문자열로 (1 → 001)."""
    return str(int(str(number).strip())).zfill(3)


def validate_hymn_number(number: str | int) -> str:
    """찬송가 1~645장 검증 후 3자리."""
    value = int(str(number).strip())
    if value < 1 or value > 645:
        raise FileMatchError("찬송가 장 번호는 1~645 사이여야 합니다.")
    return str(value).zfill(3)


def hymn_file_prefix(hymn_input: str | int) -> str:
    """'1', '1장' → '찬001_'."""
    number = validate_hymn_number(extract_number(str(hymn_input)))
    return f"찬{number}_"


SHOW_EXTENSIONS = (".ppsx", ".pps", ".pptx", ".ppt")


def _pick_by_extension(
    candidates: list[Path],
    extensions: tuple[str, ...],
    *,
    label: str = "파일",
) -> Path:
    for ext in extensions:
        group = [p for p in candidates if p.suffix.lower() == ext]
        if len(group) == 1:
            return group[0]
        if len(group) > 1:
            raise FileMatchError(
                f"{label}이(가) {len(group)}개 있습니다. 하나를 선택해 주세요.",
                [p.name for p in group],
            )
    if len(candidates) == 1:
        return candidates[0]
    raise FileMatchError(
        f"{label}이(가) {len(candidates)}개 있습니다. 하나를 선택해 주세요.",
        [p.name for p in candidates],
    )


def find_hymn_file(directory: Path, hymn_input: str) -> Path:
    """찬송가 PPT 폴더에서 '찬{3자리}_' 접두로 파일 검색."""
    if not directory.is_dir():
        raise FileMatchError(f"찬송가 PPT 폴더를 찾을 수 없습니다: {directory}")

    prefix = hymn_file_prefix(hymn_input)
    candidates = sorted(
        p for p in directory.iterdir() if p.is_file() and p.name.startswith(prefix)
    )
    if not candidates:
        raise FileMatchError(
            f"찬송가 PPT 폴더에 '{prefix}'로 시작하는 파일이 없습니다.",
            [],
        )
    if len(candidates) > 1:
        raise FileMatchError(
            f"'{prefix}'로 시작하는 찬송가 파일이 {len(candidates)}개 있습니다. 하나를 선택해 주세요.",
            [c.name for c in candidates],
        )
    return candidates[0]


def find_hymn_slideshow_file(directory: Path, hymn_input: str) -> Path:
    """찬송가 슬라이드쇼 폴더에서 ppsx/pptx 파일 검색 (.ppsx 우선)."""
    if not directory.is_dir():
        raise FileMatchError(f"찬송가 슬라이드쇼 폴더를 찾을 수 없습니다: {directory}")

    prefix = hymn_file_prefix(hymn_input)
    candidates = sorted(
        p
        for p in directory.iterdir()
        if p.is_file()
        and p.name.startswith(prefix)
        and p.suffix.lower() in SHOW_EXTENSIONS
    )
    if not candidates:
        raise FileMatchError(
            f"찬송가 슬라이드쇼 폴더에 '{prefix}'로 시작하는 ppsx/pptx 파일이 없습니다.",
            [],
        )
    return _pick_by_extension(candidates, SHOW_EXTENSIONS, label="찬송가")


def find_responsive_slideshow_file(directory: Path, number_input: str) -> Path:
    """교독문 슬라이드쇼 폴더에서 ppsx/pptx 파일 검색 (.ppsx 우선)."""
    if not directory.is_dir():
        raise FileMatchError(f"교독문 슬라이드쇼 폴더를 찾을 수 없습니다: {directory}")

    number = pad_number(extract_number(number_input))
    prefixes = [
        f"교독문{number}_",
        f"교{number}_",
        f"교독{number}_",
    ]
    candidates = sorted(
        p
        for p in directory.iterdir()
        if p.is_file()
        and p.suffix.lower() in SHOW_EXTENSIONS
        and any(p.name.startswith(prefix) for prefix in prefixes)
    )
    if not candidates:
        raise FileMatchError(
            f"교독문 슬라이드쇼 폴더에 '{number_input}'(번호 {number})에 해당하는 ppsx/pptx 파일이 없습니다.",
            [],
        )
    return _pick_by_extension(candidates, SHOW_EXTENSIONS, label="교독문")


def find_responsive_file(directory: Path, number_input: str) -> Path:
    """교독문 PPT 폴더에서 '교독문{3자리}_' 접두로 파일 검색."""
    if not directory.is_dir():
        raise FileMatchError(f"교독문 PPT 폴더를 찾을 수 없습니다: {directory}")

    number = pad_number(extract_number(number_input))
    prefixes = [
        f"교독문{number}_",
        f"교{number}_",
        f"교독{number}_",
    ]
    candidates: list[Path] = []
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        name = path.name
        if any(name.startswith(p) for p in prefixes):
            candidates.append(path)

    if not candidates:
        raise FileMatchError(
            f"교독문 PPT 폴더에서 '{number_input}'(번호 {number})에 해당하는 파일을 찾을 수 없습니다. "
            f"(예: '교독문{number}_'로 시작)",
            [],
        )
    if len(candidates) > 1:
        raise FileMatchError(
            f"교독문 번호 '{number_input}'에 해당하는 파일이 {len(candidates)}개 있습니다.",
            [c.name for c in candidates],
        )
    return candidates[0]
