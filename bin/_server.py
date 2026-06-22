"""bin/*.bat 공용 — 프로젝트 루트 기준 서버 제어."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "app" / "data" / "runtime_settings.json"


def load_port() -> int:
    if SETTINGS.is_file():
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
        return int(data.get("port", 8000))
    return 8000


def load_host() -> str:
    if SETTINGS.is_file():
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
        host = str(data.get("host", "127.0.0.1"))
        if host in ("0.0.0.0", "::"):
            return "127.0.0.1"
        return host
    return "127.0.0.1"


def find_listening_pids(port: int) -> list[int]:
    if sys.platform != "win32":
        return []
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True,
        text=True,
        encoding="cp949",
        errors="replace",
    )
    needle = f":{port}"
    pids: list[int] = []
    seen: set[int] = set()
    for line in result.stdout.splitlines():
        if "LISTENING" not in line or needle not in line:
            continue
        parts = line.split()
        if not parts:
            continue
        try:
            pid = int(parts[-1])
        except ValueError:
            continue
        if pid not in seen:
            seen.add(pid)
            pids.append(pid)
    return pids


def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        return sock.connect_ex((host, port)) == 0


def resolve_python() -> Path:
    venv_py = ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_py.is_file():
        return venv_py
    return Path(sys.executable)


def cmd_port() -> int:
    print(load_port())
    return 0


def cmd_running() -> int:
    host, port = load_host(), load_port()
    print("yes" if is_port_open(host, port) else "no")
    return 0


def cmd_kill() -> int:
    port = load_port()
    pids = find_listening_pids(port)
    if not pids:
        print("not_running")
        return 0
    if sys.platform != "win32":
        print("unsupported")
        return 1
    for pid in pids:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True,
            text=True,
        )
    print("stopped")
    return 0


def cmd_wait_free(timeout: float = 20.0) -> int:
    host, port = load_host(), load_port()
    import time

    deadline = time.time() + timeout
    while time.time() < deadline:
        if not is_port_open(host, port):
            print("free")
            return 0
        time.sleep(0.5)
    print("busy")
    return 1


def cmd_admin_check() -> int:
    sys.path.insert(0, str(ROOT))
    from app.auth_service import ensure_db, is_password_configured
    from app.config import settings
    from app.database import get_connection

    ensure_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT username, password_hash, updated_at FROM admin WHERE username = ?",
            (settings.admin_username,),
        ).fetchone()

    configured = is_password_configured()
    print(f"아이디: {settings.admin_username}")
    print(f"비밀번호 설정됨: {'예' if configured else '아니오'}")
    if row and row["password_hash"]:
        stored = str(row["password_hash"]).strip()
        print(f"해시 형식: bcrypt ({stored[:4]}..., 길이 {len(stored)})")
        print(f"마지막 변경: {row['updated_at']}")
    else:
        print("해시: 없음")
    print(f"DB: {ROOT / 'app' / 'data' / 'worship.db'}")
    return 0


def cmd_admin_reset() -> int:
    sys.path.insert(0, str(ROOT))
    from datetime import datetime, timezone

    from app.config import settings
    from app.database import get_connection, init_db

    init_db(settings.admin_username)
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions")
        conn.execute(
            "UPDATE admin SET password_hash = NULL, updated_at = ? WHERE username = ?",
            (now, settings.admin_username),
        )
    print("관리자 비밀번호를 초기화했습니다.")
    print("브라우저에서 /login 을 새로고침하면 설정 화면이 나옵니다.")
    return 0


def cmd_status() -> int:
    host, port = load_host(), load_port()
    pids = find_listening_pids(port)
    running = is_port_open(host, port)

    print(f"프로젝트: {ROOT}")
    print(f"주소: http://{host}:{port}")
    print(f"포트: {port}")
    print(f"상태: {'실행 중' if running else '중지됨'}")
    if pids:
        print(f"PID: {', '.join(str(p) for p in pids)}")

    if not running:
        return 0

    try:
        with urllib.request.urlopen(f"http://{host}:{port}/api/server/status", timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
        print(f"모드: {data.get('mode_label', '-')}")
        print(f"가동: {data.get('uptime_seconds', 0)}초")
        print(f"URL: {data.get('url', '-')}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        print("API: 응답 없음 (구버전이거나 기동 중일 수 있음)")

    try:
        with urllib.request.urlopen(f"http://{host}:{port}/health", timeout=3) as res:
            health = json.loads(res.read().decode("utf-8"))
        print(f"버전: {health.get('version', '-')}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        pass

    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: port|running|kill|wait|status|admin-check|admin-reset", file=sys.stderr)
        return 2
    cmd = sys.argv[1]
    if cmd == "port":
        return cmd_port()
    if cmd == "running":
        return cmd_running()
    if cmd == "kill":
        return cmd_kill()
    if cmd == "wait":
        return cmd_wait_free()
    if cmd == "status":
        return cmd_status()
    if cmd == "admin-check":
        return cmd_admin_check()
    if cmd == "admin-reset":
        return cmd_admin_reset()
    print(f"unknown: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
