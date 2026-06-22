"""자동 테스트 — 경로·API·파일 매칭·(가능 시) COM 환경."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402
from app.engines.file_matcher import find_hymn_file, find_responsive_file  # noqa: E402


@dataclass
class TestResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class TestReport:
    results: list[TestResult] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        self.results.append(TestResult(name, passed, detail))

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    def to_dict(self) -> dict:
        return {
            "summary": {"passed": self.passed, "failed": self.failed, "total": len(self.results)},
            "results": [{"name": r.name, "passed": r.passed, "detail": r.detail} for r in self.results],
        }


def test_paths(report: TestReport) -> None:
    checks = [
        ("주보 hwpx 템플릿", settings.hwp_template_path, settings.hwp_template_path.is_file()),
        ("낮예배 pptx 템플릿", settings.day_ppt_template_path, settings.day_ppt_template_path.is_file()),
        ("찬송가 PPT 폴더", settings.hymn_ppt_dir, settings.hymn_ppt_dir.is_dir()),
        ("교독문 PPT 폴더", settings.responsive_ppt_dir, settings.responsive_ppt_dir.is_dir()),
    ]
    for label, path, ok in checks:
        report.add(f"경로: {label}", ok, str(path))


def test_file_matcher(report: TestReport) -> None:
    try:
        hymn = find_hymn_file(settings.hymn_ppt_dir, "1장")
        report.add("찬송가 매칭 (1장)", hymn.name.startswith("찬001_"), hymn.name)
    except Exception as exc:
        report.add("찬송가 매칭 (1장)", False, str(exc))

    try:
        resp = find_responsive_file(settings.responsive_ppt_dir, "1번")
        report.add("교독문 매칭 (1번)", resp.name.startswith("교독문001_"), resp.name)
    except Exception as exc:
        report.add("교독문 매칭 (1번)", False, str(exc))

    try:
        resp35 = find_responsive_file(settings.responsive_ppt_dir, "35번")
        report.add("교독문 매칭 (35번)", "035" in resp35.name or "35" in resp35.name, resp35.name)
    except Exception as exc:
        report.add("교독문 매칭 (35번)", False, str(exc))


def test_mail_merge_fields(report: TestReport) -> None:
    path = ROOT / "app" / "data" / "mail_merge_fields.json"
    if not path.is_file():
        report.add("메일머지 필드 JSON", False, "파일 없음")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    ok = len(data) >= 60
    report.add("메일머지 필드 JSON", ok, f"{len(data)}개 필드")


def test_section_config(report: TestReport) -> None:
    path = ROOT / "app" / "section_config" / "sunday_day.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    sections = data.get("sections", [])
    report.add("sunday_day.json 구역 정의", len(sections) == 8, f"{len(sections)}개 구역")


def test_api(base_url: str, report: TestReport) -> None:
    def get(path: str) -> tuple[int, dict | str]:
        req = urllib.request.Request(base_url + path)
        with urllib.request.urlopen(req, timeout=10) as res:
            body = res.read().decode("utf-8")
            try:
                return res.status, json.loads(body)
            except json.JSONDecodeError:
                return res.status, body

    try:
        status, body = get("/health")
        report.add("API /health", status == 200 and body.get("status") == "ok", str(body))
    except urllib.error.URLError as exc:
        report.add("API /health", False, f"서버 미실행: {exc}")
        return

    try:
        status, body = get("/api/bulletin/fields")
        count = len(body.get("fields", [])) if isinstance(body, dict) else 0
        report.add("API /api/bulletin/fields", status == 200 and count == 65, f"{count}개")
    except Exception as exc:
        report.add("API /api/bulletin/fields", False, str(exc))

    try:
        status, body = get("/api/settings/paths")
        paths = body.get("paths", []) if isinstance(body, dict) else []
        all_ok = all(p.get("exists") for p in paths)
        report.add("API /api/settings/paths", status == 200 and all_ok, f"{sum(p.get('exists') for p in paths)}/{len(paths)} OK")
    except Exception as exc:
        report.add("API /api/settings/paths", False, str(exc))

    try:
        status, body = get("/api/settings/runtime")
        report.add(
            "API /api/settings/runtime",
            status == 200 and body.get("run_mode") in ("development", "production"),
            body.get("mode_label", ""),
        )
    except Exception as exc:
        report.add("API /api/settings/runtime", False, str(exc))

    try:
        status, body = get("/api/server/status")
        report.add(
            "API /api/server/status",
            status == 200 and body.get("status") == "running",
            f"uptime={body.get('uptime_seconds', 0)}s",
        )
    except Exception as exc:
        report.add("API /api/server/status", False, str(exc))

    try:
        status, body = get("/api/outlines/schema")
        count = len(body.get("fields", [])) if isinstance(body, dict) else 0
        report.add("API /api/outlines/schema", status == 200 and count > 0, f"{count}개")
    except Exception as exc:
        report.add("API /api/outlines/schema", False, str(exc))

    try:
        status, body = get("/api/favorites")
        count = len(body.get("items", [])) if isinstance(body, dict) else 0
        report.add("API /api/favorites", status == 200 and count > 0, f"{count}개")
    except Exception as exc:
        report.add("API /api/favorites", False, str(exc))


def test_hwp_install(report: TestReport) -> None:
    hwp = Path(r"C:\Program Files (x86)\HNC\Office 2024\HOffice130\Bin\Hwp.exe")
    report.add("한글(Hwp.exe) 설치", hwp.is_file(), str(hwp))


def test_com(report: TestReport) -> None:
    try:
        import win32com.client as win32
    except ImportError:
        report.add("pywin32 설치", False, "pip install pywin32 필요")
        return
    report.add("pywin32 설치", True, "")

    try:
        ppt = win32.gencache.EnsureDispatch("PowerPoint.Application")
        ver = ppt.Version
        ppt.Quit()
        report.add("PowerPoint COM", True, f"버전 {ver}")
    except Exception as exc:
        report.add("PowerPoint COM", False, str(exc))

    try:
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        hwp.Quit()
        report.add("한글 COM", True, "")
    except Exception as exc:
        report.add("한글 COM", False, str(exc))


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    report = TestReport()
    test_paths(report)
    test_file_matcher(report)
    test_mail_merge_fields(report)
    test_section_config(report)
    test_hwp_install(report)
    test_com(report)
    test_api(base_url, report)

    out_path = ROOT / "app" / "data" / "test_report.json"
    out_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
