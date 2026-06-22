"""인증 미들웨어 — 페이지는 로그인으로, API는 401."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from app.auth_service import (
    SESSION_COOKIE,
    delete_session,
    get_session_user,
    is_password_configured,
    purge_expired_sessions,
)

_PUBLIC_EXACT = {
    "/login",
    "/health",
    "/favicon.ico",
}

_SETUP_AUTH_PATHS = {
    "/api/auth/status",
    "/api/auth/setup",
}


def _is_auth_public(path: str) -> bool:
    if path in _SETUP_AUTH_PATHS:
        return True
    if not path.startswith("/api/auth/"):
        return False
    return is_password_configured()


def _is_public(path: str) -> bool:
    if path in _PUBLIC_EXACT:
        return True
    if path.startswith("/static/"):
        return True
    return _is_auth_public(path)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        purge_expired_sessions()

        path = request.url.path
        token = request.cookies.get(SESSION_COOKIE)
        password_ready = is_password_configured()

        if not password_ready and token:
            delete_session(token)
            token = None

        username = get_session_user(token) if password_ready else None
        if username:
            request.state.user = username

        if _is_public(path):
            return await call_next(request)

        if username:
            return await call_next(request)

        if path.startswith("/api/"):
            detail = (
                "먼저 관리자 비밀번호를 설정해 주세요."
                if not password_ready
                else "로그인이 필요합니다."
            )
            status = 400 if not password_ready else 401
            return JSONResponse(status_code=status, content={"detail": detail})

        next_url = request.url.path
        if request.url.query:
            next_url = f"{next_url}?{request.url.query}"
        return RedirectResponse(url=f"/login?next={next_url}", status_code=302)
