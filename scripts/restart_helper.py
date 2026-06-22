"""서버 종료 후 start.py를 다시 실행한다."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.runtime_settings import load_runtime_settings  # noqa: E402


def wait_for_port_free(host: str, port: int, timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) != 0:
                return True
        time.sleep(0.5)
    return False


def main() -> None:
    time.sleep(2)
    rt = load_runtime_settings()
    wait_for_port_free(rt.host, rt.port)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    subprocess.Popen(
        [sys.executable, str(ROOT / "start.py")],
        cwd=ROOT,
        env=env,
        creationflags=creationflags,
        close_fds=os.name != "nt",
    )


if __name__ == "__main__":
    main()
