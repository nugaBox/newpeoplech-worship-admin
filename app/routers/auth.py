"""관리자 로그인 API."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from app.auth_service import (
    SESSION_COOKIE,
    authenticate,
    change_admin_password,
    create_session,
    delete_session,
    is_password_configured,
    set_admin_password,
)
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AuthStatusResponse(BaseModel):
    password_configured: bool
    username: str


class SetupPasswordRequest(BaseModel):
    password: str = Field(min_length=4, max_length=128)
    password_confirm: str = Field(min_length=4, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)
    remember: bool = False


class AuthUserResponse(BaseModel):
    username: str


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=4, max_length=128)
    new_password_confirm: str = Field(min_length=4, max_length=128)


class MessageResponse(BaseModel):
    message: str


def _set_session_cookie(response: Response, token: str, expires_at: datetime) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        expires=expires_at,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE, path="/")


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status() -> AuthStatusResponse:
    return AuthStatusResponse(
        password_configured=is_password_configured(),
        username=settings.admin_username,
    )


@router.post("/setup", response_model=AuthUserResponse)
async def setup_password(body: SetupPasswordRequest, response: Response) -> AuthUserResponse:
    if is_password_configured():
        raise HTTPException(status_code=400, detail="이미 관리자 비밀번호가 설정되어 있습니다.")
    if body.password != body.password_confirm:
        raise HTTPException(status_code=400, detail="비밀번호 확인이 일치하지 않습니다.")

    set_admin_password(body.password)
    token, expires_at = create_session(settings.admin_username, remember=True)
    _set_session_cookie(response, token, expires_at)
    return AuthUserResponse(username=settings.admin_username)


@router.post("/login", response_model=AuthUserResponse)
async def login(body: LoginRequest, response: Response) -> AuthUserResponse:
    if not is_password_configured():
        raise HTTPException(status_code=400, detail="먼저 관리자 비밀번호를 설정해 주세요.")
    if body.username != settings.admin_username:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    if not authenticate(body.username, body.password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    token, expires_at = create_session(body.username, remember=body.remember)
    _set_session_cookie(response, token, expires_at)
    return AuthUserResponse(username=body.username)


@router.post("/logout")
async def logout(request: Request, response: Response) -> dict[str, str]:
    delete_session(request.cookies.get(SESSION_COOKIE))
    _clear_session_cookie(response)
    return {"message": "로그아웃되었습니다."}


@router.get("/me", response_model=AuthUserResponse)
async def current_user(request: Request) -> AuthUserResponse:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return AuthUserResponse(username=user)


@router.post("/password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest, request: Request
) -> MessageResponse:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    if not is_password_configured():
        raise HTTPException(status_code=400, detail="관리자 비밀번호가 설정되어 있지 않습니다.")
    if body.new_password != body.new_password_confirm:
        raise HTTPException(status_code=400, detail="새 비밀번호 확인이 일치하지 않습니다.")
    if not change_admin_password(body.current_password, body.new_password):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 올바르지 않습니다.")
    return MessageResponse(message="비밀번호가 변경되었습니다.")
