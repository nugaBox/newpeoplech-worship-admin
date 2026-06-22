"""런타임 설정 (개발/운영 모드 등) — JSON 파일 저장."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent / "data"
SETTINGS_FILE = DATA_DIR / "runtime_settings.json"


class RunMode(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class RuntimeSettings(BaseModel):
    run_mode: RunMode = RunMode.DEVELOPMENT
    host: str = "127.0.0.1"
    port: int = 8000
    open_browser: bool = True

    @property
    def is_development(self) -> bool:
        return self.run_mode == RunMode.DEVELOPMENT

    @property
    def mode_label(self) -> str:
        return "개발모드" if self.is_development else "운영모드"


def load_runtime_settings() -> RuntimeSettings:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_FILE.is_file():
        default = RuntimeSettings()
        save_runtime_settings(default)
        return default
    data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    return RuntimeSettings.model_validate(data)


def save_runtime_settings(settings: RuntimeSettings) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        settings.model_dump_json(indent=2),
        encoding="utf-8",
    )
