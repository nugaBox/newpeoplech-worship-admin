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


def pad_hymn_number(number: str) -> str:
    return str(int(number)).zfill(3)


def find_hymn_file(directory: Path, hymn_input: str) -> Path:
    """찬송가 PPT 폴더에서 '찬{3자리}_' 접두로 파일 검색."""
    if not directory.is_dir():
        raise FileMatchError(f"찬송가 PPT 폴더를 찾을 수 없습니다: {directory}")

    number = pad_hymn_number(extract_number(hymn_input))
    prefix = f"찬{number}_"
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


def find_responsive_file(directory: Path, number_input: str) -> Path:
    """교독문 PPT 폴더에서 '교독문{3자리}_' 접두로 파일 검색."""
    if not directory.is_dir():
        raise FileMatchError(f"교독문 PPT 폴더를 찾을 수 없습니다: {directory}")

    number = pad_hymn_number(extract_number(number_input))
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
