"""
서버 시작 진입점.

터미널에서 한 번만 실행하면 됩니다:
    python start.py

이후에는 크롬 브라우저(또는 크롬 웹앱)로 접속해 사용합니다.
재시작은 웹 UI 설정 화면에서 할 수 있습니다.
"""

from __future__ import annotations

import os
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from app.runtime_settings import load_runtime_settings  # noqa: E402


def _find_listening_pid(port: int) -> int | None:
    """Windows: 포트를 점유 중인 LISTENING 프로세스 PID."""
    if os.name != "nt":
        return None
    import subprocess

    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True,
        text=True,
        encoding="cp949",
        errors="replace",
    )
    needle = f":{port}"
    for line in result.stdout.splitlines():
        if "LISTENING" not in line or needle not in line:
            continue
        parts = line.split()
        if parts:
            try:
                return int(parts[-1])
            except ValueError:
                continue
    return None


def main() -> None:
    import socket
    import uvicorn

    rt = load_runtime_settings()
    url = f"http://{rt.host}:{rt.port}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if sock.connect_ex((rt.host, rt.port)) == 0:
            pid = _find_listening_pid(rt.port)
            print(f"\n[오류] 포트 {rt.port}이(가) 이미 사용 중입니다.")
            if pid:
                print(f"  - 점유 프로세스 PID: {pid}")
                print(f"  - 종료: taskkill /F /T /PID {pid}")
            print("  - 설정 > 서버에서 중지/재시작을 누르거나")
            print("  - 이전에 켜 둔 터미널/서버를 종료한 뒤 다시 실행하세요.")
            print(f"  - 긴급 제어: 브라우저에서 {url}/control")
            print(f"  - 또는 설정에서 포트를 바꾼 뒤 재시작하세요.\n")
            raise SystemExit(1)

    if rt.open_browser:
        webbrowser.open(url)

    reload_dirs = [str(ROOT / d) for d in ("app", "templates", "static")]
    uvicorn.run(
        "app.main:app",
        host=rt.host,
        port=rt.port,
        reload=rt.is_development,
        reload_dirs=reload_dirs if rt.is_development else None,
    )


if __name__ == "__main__":
    main()
