"""관리자 인증 — 비밀번호 해시, 세션 토큰."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt

from app.config import settings
from app.database import get_connection, init_db

SESSION_COOKIE = "worship_session"
SESSION_HOURS = 12
REMEMBER_DAYS = 30


def ensure_db() -> None:
    init_db(settings.admin_username)


def is_password_configured() -> bool:
    ensure_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT password_hash FROM admin WHERE username = ?",
            (settings.admin_username,),
        ).fetchone()
    if not row:
        return False
    password_hash = row["password_hash"]
    if not password_hash or not str(password_hash).strip():
        return False
    # bcrypt 해시만 유효한 설정으로 인정
    stored = str(password_hash).strip()
    return stored.startswith("$2") and len(stored) >= 60


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def set_admin_password(password: str) -> None:
    ensure_db()
    now = datetime.now(timezone.utc).isoformat()
    password_hash = hash_password(password)
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE admin
            SET password_hash = ?, updated_at = ?
            WHERE username = ?
            """,
            (password_hash, now, settings.admin_username),
        )


def change_admin_password(current_password: str, new_password: str) -> bool:
    if not authenticate(settings.admin_username, current_password):
        return False
    set_admin_password(new_password)
    return True


def authenticate(username: str, password: str) -> bool:
    ensure_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT password_hash FROM admin WHERE username = ?",
            (username,),
        ).fetchone()
    if not row or not row["password_hash"]:
        return False
    return verify_password(password, row["password_hash"])


def create_session(username: str, *, remember: bool) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    if remember:
        expires_at = datetime.now(timezone.utc) + timedelta(days=REMEMBER_DAYS)
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_HOURS)
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (token, username, expires_at, remember, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (token, username, expires_at.isoformat(), int(remember), now),
        )
    return token, expires_at


def get_session_user(token: str | None) -> str | None:
    if not token:
        return None
    ensure_db()
    now = datetime.now(timezone.utc)
    with get_connection() as conn:
        row = conn.execute(
            "SELECT username, expires_at FROM sessions WHERE token = ?",
            (token,),
        ).fetchone()
        if not row:
            return None
        expires_at = datetime.fromisoformat(row["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= now:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            return None
        return row["username"]


def delete_session(token: str | None) -> None:
    if not token:
        return
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def purge_expired_sessions() -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
