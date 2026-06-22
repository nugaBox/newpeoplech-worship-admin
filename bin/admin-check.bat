@echo off
setlocal EnableExtensions
chcp 65001 >nul
call "%~dp0_env.bat" || exit /b 1

echo.
echo ========================================
echo   예배 준비실 — 관리자 비밀번호 확인
echo ========================================
echo.
"%PY%" "%CTL%" admin-check
echo.
pause
