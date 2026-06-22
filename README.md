# newpeoplech-worship-admin

광주새백성교회(newpeoplech) 예배 관리 프로그램.

## 상태

✅ 0.2 — NUGABOX 관리자 템플릿 기반 UI

| 메뉴 | 기능 |
|---|---|
| **홈** | 즐겨찾기 폴더·파일 바로 열기 |
| **예배 관리** | 저장된 목차 선택 → 주보/PPT 생성 |
| **목차 관리** | 주일낮·찬양예배 필드 입력·저장 |
| **설정** (사이드바 하단) | 서버, 경로, 실행 모드, 즐겨찾기 편집 |

## 실행

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python start.py
```

크롬에서 `http://127.0.0.1:8000` → 앱 설치(PWA) 후 사용.

> 한글/PowerPoint COM 생성은 Windows + 한글/PowerPoint 설치 PC에서만 동작합니다.
