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

크롬에서 `http://127.0.0.1:8000` 또는 `https://worship.newpeoplech.com` → 앱 설치(PWA) 후 사용.

### nginx 역방향 프록시

예배 준비실 PC에서 `python start.py`로 서버를 띄운 뒤, nginx가 `127.0.0.1:8000`으로 프록시합니다.

```bash
# Linux
sudo cp deploy/nginx-worship.conf /etc/nginx/sites-available/worship.newpeoplech.com
sudo ln -sf /etc/nginx/sites-available/worship.newpeoplech.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

```bat
REM Windows (nginx 설치 경로에 맞게 수정)
copy deploy\nginx-worship.conf C:\nginx\conf\conf.d\worship.newpeoplech.com.conf
nginx -t && nginx -s reload
```

`.env` (이미 기본값 포함):

```env
PUBLIC_URL=https://worship.newpeoplech.com
TRUST_PROXY_HEADERS=true
FORWARDED_ALLOW_IPS=127.0.0.1
```

- nginx와 FastAPI가 **같은 PC**면 `deploy/nginx-worship.conf`의 `upstream`을 그대로 씁니다.
- nginx가 **다른 서버**면 `upstream` 주소를 예배 PC IP로 바꾸고, `.env`의 `FORWARDED_ALLOW_IPS`를 `*` 또는 nginx 서버 IP로 설정하세요.
- 원격에서 예배 PC에 직접 붙이려면 설정 > 실행 모드에서 주소를 `0.0.0.0`으로 바꾼 뒤 재시작합니다.

> 한글/PowerPoint COM 생성은 Windows + 한글/PowerPoint 설치 PC에서만 동작합니다.
