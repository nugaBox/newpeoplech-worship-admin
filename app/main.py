"""FastAPI 엔트리포인트."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import bulletin, favorites, outlines, server, settings
from app.server_control import mark_server_started

ROOT_DIR = Path(__file__).resolve().parent.parent
FAVICON_DIR = ROOT_DIR / "static" / "images" / "favicon"
FAVICON_ICO = FAVICON_DIR / "favicon.ico"


@asynccontextmanager
async def lifespan(app: FastAPI):
    mark_server_started()
    yield


app = FastAPI(
    title="광주새백성교회 예배 관리",
    description="주보/PPT 생성 로컬 웹서비스",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(bulletin.router)
app.include_router(settings.router)
app.include_router(server.router)
app.include_router(favorites.router)
app.include_router(outlines.router)

static_dir = ROOT_DIR / "static"
templates_dir = ROOT_DIR / "templates"

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=str(templates_dir))


def _page(request: Request, name: str, title: str, nav: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name=name,
        context={"page_title": title, "active_nav": nav},
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return _page(request, "home.html", "홈", "home")


@app.get("/worship", response_class=HTMLResponse)
async def worship_page(request: Request) -> HTMLResponse:
    return _page(request, "worship.html", "예배 관리", "worship")


@app.get("/outline", response_class=HTMLResponse)
async def outline_page(request: Request) -> HTMLResponse:
    return _page(request, "outline.html", "목차 관리", "outline")


@app.get("/settings")
async def settings_redirect() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=302)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse(FAVICON_ICO, media_type="image/x-icon")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.get("/control", response_class=HTMLResponse)
async def control_page() -> HTMLResponse:
    """템플릿 오류 시에도 접근 가능한 최소 서버 제어 화면."""
    return HTMLResponse(
        """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#10A37F">
  <title>서버 제어 — 예배 관리</title>
  <link rel="icon" href="/static/images/favicon/favicon.ico" sizes="any">
  <link rel="icon" href="/static/images/favicon/favicon.svg" type="image/svg+xml">
  <style>
    body { font-family: system-ui, sans-serif; max-width: 480px; margin: 48px auto; padding: 0 16px; }
    h1 { font-size: 1.25rem; }
    .status { color: #555; margin: 12px 0 20px; }
    button { margin-right: 8px; margin-bottom: 8px; padding: 8px 14px; cursor: pointer; }
    .danger { color: #b42318; border-color: #b42318; }
    #msg { margin-top: 16px; font-size: 14px; color: #333; }
  </style>
</head>
<body>
  <h1>서버 제어</h1>
  <div class="status" id="status">상태 확인 중...</div>
  <button type="button" id="btn-restart">재시작</button>
  <button type="button" id="btn-stop" class="danger">중지</button>
  <button type="button" onclick="location.href='/'">홈으로</button>
  <div id="msg"></div>
  <script>
    const msg = (t) => { document.getElementById("msg").textContent = t; };
    async function refresh() {
      const el = document.getElementById("status");
      try {
        const r = await fetch("/api/server/status");
        if (!r.ok) throw new Error("status " + r.status);
        const d = await r.json();
        el.textContent = d.mode_label + " · " + d.url + " · 가동 " + d.uptime_seconds + "초";
      } catch {
        el.textContent = "서버 API에 연결할 수 없습니다. 구버전이거나 중지된 상태일 수 있습니다.";
      }
    }
    document.getElementById("btn-restart").onclick = async () => {
      if (!confirm("서버를 재시작합니다. 잠시 연결이 끊깁니다.")) return;
      msg("재시작 중...");
      await fetch("/api/server/restart", { method: "POST" });
      for (let i = 0; i < 30; i++) {
        await new Promise((r) => setTimeout(r, 1000));
        try {
          await fetch("/api/server/status");
          msg("재시작 완료. 홈으로 이동합니다.");
          location.href = "/";
          return;
        } catch {}
      }
      msg("재시작 대기 시간 초과. 페이지를 새로고침하세요.");
    };
    document.getElementById("btn-stop").onclick = async () => {
      if (!confirm("서버를 중지합니다. 터미널에서 python start.py 로 다시 켜야 합니다.")) return;
      msg("중지 중...");
      await fetch("/api/server/stop", { method: "POST" });
      msg("서버가 중지되었습니다.");
      document.getElementById("status").textContent = "중지됨";
    };
    refresh();
  </script>
</body>
</html>"""
    )
