"""Windows 네이티브 폴더·파일 선택 대화상자."""

from __future__ import annotations

import sys
from typing import Literal

PathKind = Literal["file", "dir"]


def pick_path(*, kind: PathKind, initial_dir: str | None = None) -> str | None:
    """로컬 PC에서 폴더 또는 파일을 고른다. 취소 시 None."""
    if sys.platform != "win32":
        raise OSError("폴더·파일 찾기는 Windows에서만 지원합니다.")

    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    try:
        if kind == "file":
            selected = filedialog.askopenfilename(initialdir=initial_dir or None)
        else:
            selected = filedialog.askdirectory(initialdir=initial_dir or None)
        return selected or None
    finally:
        root.destroy()
