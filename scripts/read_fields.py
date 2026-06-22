"""임시: 메일머지 필드 목록 추출"""
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

path = Path(r"C:\Users\churchCom\Documents\churchCloud\교회 문서\03 주보\주보_메일머지필드.xlsx")
out = Path(__file__).resolve().parents[1] / "app" / "data" / "mail_merge_fields.json"

with zipfile.ZipFile(path) as z:
    shared: list[str] = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        for si in root.findall(".//m:si", ns):
            texts = [t.text or "" for t in si.findall(".//m:t", ns)]
            shared.append("".join(texts))
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rows: list[list[str]] = []
    for row in sheet.findall(".//m:sheetData/m:row", ns):
        vals: list[str] = []
        for c in row.findall("m:c", ns):
            t = c.get("t")
            v = c.find("m:v", ns)
            if v is None:
                continue
            if t == "s":
                vals.append(shared[int(v.text)])
            else:
                vals.append(v.text or "")
        if vals:
            rows.append(vals)

fields = rows[0]
samples = rows[1] if len(rows) > 1 else []
out.parent.mkdir(parents=True, exist_ok=True)
payload = [{"field": f, "sample": samples[i] if i < len(samples) else ""} for i, f in enumerate(fields)]
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {len(fields)} fields to {out}")
