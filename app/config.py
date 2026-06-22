"""환경 설정 및 경로 검증."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    hwp_template_path: Path = Path(
        r"C:\Users\churchCom\Documents\churchCloud\교회 문서\03 주보\광주새백성교회_주보_2026_메일머지.hwpx"
    )
    day_ppt_template_path: Path = Path(
        r"C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\주일낮예배-2026-템플릿.pptx"
    )
    hymn_ppt_dir: Path = Path(
        r"C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\찬송가 PPT"
    )
    responsive_ppt_dir: Path = Path(
        r"C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\교독문 PPT"
    )
    output_dir: Path = ROOT_DIR / "app" / "data" / "output"

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
