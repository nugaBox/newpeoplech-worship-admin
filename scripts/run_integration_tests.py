"""HWP/PPT 생성 통합 테스트 (Windows + COM 필요)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402
from app.engines.hwp_engine import generate_bulletin_hwp  # noqa: E402
from app.engines.ppt_engine import generate_day_ppt  # noqa: E402


def main() -> int:
    fields_path = ROOT / "app" / "data" / "mail_merge_fields.json"
    fields = {
        item["field"]: item.get("sample", "") or ""
        for item in json.loads(fields_path.read_text(encoding="utf-8"))
    }
    out_dir = settings.ensure_output_dir()
    results: list[tuple[str, bool, str]] = []

    hwp_out = out_dir / "integration_test_bulletin.hwpx"
    try:
        generate_bulletin_hwp(settings.hwp_template_path, hwp_out, fields)
        ok = hwp_out.is_file() and hwp_out.stat().st_size > 1000
        results.append(("HWP 생성", ok, f"{hwp_out.name} ({hwp_out.stat().st_size if ok else 0} bytes)"))
    except Exception as exc:
        results.append(("HWP 생성", False, str(exc)))

    ppt_out = out_dir / "integration_test_day.pptx"
    try:
        warnings = generate_day_ppt(
            template_path=settings.day_ppt_template_path,
            output_path=ppt_out,
            fields=fields,
            hymn_dir=settings.hymn_ppt_dir,
            responsive_dir=settings.responsive_ppt_dir,
        )
        ok = ppt_out.is_file() and ppt_out.stat().st_size > 1000
        detail = f"{ppt_out.name}; warnings={len(warnings)}"
        results.append(("낮예배 PPT 생성", ok, detail))
    except Exception as exc:
        results.append(("낮예배 PPT 생성", False, str(exc)))

    report = {"results": [{"name": n, "passed": p, "detail": d} for n, p, d in results]}
    out = ROOT / "app" / "data" / "integration_test_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(r["passed"] for r in report["results"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
