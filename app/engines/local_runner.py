"""로컬 폴더·파일 실행."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def open_path(target: Path) -> None:
    """Windows 탐색기 또는 기본 프로그램으로 경로를 연다."""
    if not target.exists():
        raise FileNotFoundError(f"경로를 찾을 수 없습니다: {target}")

    if sys.platform == "win32":
        os.startfile(str(target))  # noqa: S606
        return

    if target.is_dir():
        subprocess.Popen(["xdg-open", str(target)])
    else:
        subprocess.Popen(["xdg-open", str(target)])
