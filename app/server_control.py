"""서버 상태 추적 및 재시작."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from app.runtime_settings import RuntimeSettings, load_runtime_settings

ROOT_DIR = Path(__file__).resolve().parent.parent
RESTART_HELPER = ROOT_DIR / "scripts" / "restart_helper.py"

_server_started_at: datetime = datetime.now(timezone.utc)


def mark_server_started() -> None:
    global _server_started_at
    _server_started_at = datetime.now(timezone.utc)


def get_uptime_seconds() -> int:
    return int((datetime.now(timezone.utc) - _server_started_at).total_seconds())


def get_status_payload() -> dict:
    rt = load_runtime_settings()
    return {
        "status": "running",
        "uptime_seconds": get_uptime_seconds(),
        "host": rt.host,
        "port": rt.port,
        "url": f"http://{rt.host}:{rt.port}",
        "run_mode": rt.run_mode.value,
        "mode_label": rt.mode_label,
        "reload_enabled": rt.is_development,
        "pid": os.getpid(),
    }


def _spawn_restart_helper() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    if os.name == "nt":
        subprocess.Popen(
            f'start "" /B "{sys.executable}" "{RESTART_HELPER}"',
            shell=True,
            cwd=ROOT_DIR,
            env=env,
        )
        return
    subprocess.Popen(
        [sys.executable, str(RESTART_HELPER)],
        cwd=ROOT_DIR,
        env=env,
        start_new_session=True,
        close_fds=True,
    )


def _terminate_current_server(rt: RuntimeSettings) -> None:
    if rt.is_development and os.name == "nt":
        # uvicorn --reload: 워커의 부모(감시 프로세스)를 종료해야 포트가 해제된다.
        parent_pid = os.getppid()
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(parent_pid)],
            capture_output=True,
            text=True,
        )
        return
    os._exit(0)


def schedule_restart() -> None:
    """재시작 헬퍼를 띄운 뒤 현재 서버 프로세스를 종료한다."""

    def _restart() -> None:
        time.sleep(0.5)
        rt = load_runtime_settings()
        _spawn_restart_helper()
        _terminate_current_server(rt)

    threading.Thread(target=_restart, daemon=True).start()


def schedule_stop() -> None:
    """현재 서버 프로세스를 종료한다 (재시작 없음)."""

    def _stop() -> None:
        time.sleep(0.5)
        rt = load_runtime_settings()
        _terminate_current_server(rt)

    threading.Thread(target=_stop, daemon=True).start()
