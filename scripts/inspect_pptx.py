"""PPT 템플릿 전체 텍스트 추출"""
import json
import re
import zipfile
from pathlib import Path

pptx = Path(r"C:\Users\churchCom\Documents\churchCloud\교회 문서\■ PPT\주일낮예배-2026-템플릿.pptx")
out = Path(__file__).resolve().parents[1] / "app" / "data" / "ppt_template_texts.json"
results = []

with zipfile.ZipFile(pptx) as z:
    for name in sorted(z.namelist()):
        if not (name.startswith("ppt/slides/slide") and name.endswith(".xml")):
            continue
        content = z.read(name).decode("utf-8", errors="ignore")
        texts = re.findall(r"<a:t>([^<]*)</a:t>", content)
        joined = "".join(texts)
        if joined.strip():
            results.append({"slide": name, "text": joined})

out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {len(results)} slides to {out}")
