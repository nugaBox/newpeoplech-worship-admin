@echo off
setlocal EnableExtensions
chcp 65001 >nul
call "%~dp0_env.bat" || exit /b 1

echo.
echo ========================================
echo   예배 준비실 — 서버 상태
echo ========================================
echo.
"%PY%" "%CTL%" status
echo.
pause
