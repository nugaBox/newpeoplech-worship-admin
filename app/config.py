"""환경 설정 및 경로 검증."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.path_settings import get_resolved_path, init_path_db

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    public_url: str = ""
    trust_proxy_headers: bool = True
    forwarded_allow_ips: str = "127.0.0.1"

    admin_username: str = "admin"
    cookie_secure: bool = False

    @property
    def hwp_template_path(self) -> Path:
        return get_resolved_path("hwp_template")

    @property
    def day_ppt_template_path(self) -> Path:
        return get_resolved_path("day_ppt_template")

    @property
    def hymn_ppt_dir(self) -> Path:
        return get_resolved_path("hymn_ppt_dir")

    @property
    def responsive_ppt_dir(self) -> Path:
        return get_resolved_path("responsive_ppt_dir")

    @property
    def output_dir(self) -> Path:
        return get_resolved_path("output_dir")

    def ensure_output_dir(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir

    def validate_hwp_template(self) -> None:
        if not self.hwp_template_path.is_file():
            raise FileNotFoundError(
                f"주보 hwpx 템플릿을 찾을 수 없습니다: {self.hwp_template_path}"
            )

    def validate_day_ppt_template(self) -> None:
        if not self.day_ppt_template_path.is_file():
            raise FileNotFoundError(
                f"주일낮예배 PPT 템플릿을 찾을 수 없습니다: {self.day_ppt_template_path}"
            )

    def validate_hymn_dir(self) -> None:
        if not self.hymn_ppt_dir.is_dir():
            raise FileNotFoundError(
                f"찬송가 PPT 폴더를 찾을 수 없습니다: {self.hymn_ppt_dir}"
            )

    def validate_responsive_dir(self) -> None:
        if not self.responsive_ppt_dir.is_dir():
            raise FileNotFoundError(
                f"교독문 PPT 폴더를 찾을 수 없습니다: {self.responsive_ppt_dir}"
            )


settings = Settings()
init_path_db()
