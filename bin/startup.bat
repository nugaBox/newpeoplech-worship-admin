@echo off
setlocal EnableExtensions
chcp 65001 >nul
call "%~dp0_env.bat" || exit /b 1

for /f %%R in ('"%PY%" "%CTL%" running') do set "RUNNING=%%R"
if /I "%RUNNING%"=="yes" (
  echo.
  echo [안내] 서버가 이미 실행 중입니다. ^(포트 %PORT%^)
  echo   http://127.0.0.1:%PORT%
  echo.
  pause
  exit /b 0
)

echo.
echo ========================================
echo   예배 준비실 — 서버 시작
echo   포트: %PORT%
echo ========================================
echo.

start "예배 준비실 서버" /D "%ROOT%" "%PY%" start.py

echo 서버 창을 열었습니다.
echo 브라우저: http://127.0.0.1:%PORT%
echo.
timeout /t 3 /nobreak >nul
