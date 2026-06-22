@echo off
setlocal EnableExtensions
chcp 65001 >nul
call "%~dp0_env.bat" || exit /b 1

echo.
echo ========================================
echo   예배 준비실 — 서버 재시작
echo   포트: %PORT%
echo ========================================
echo.

for /f %%R in ('"%PY%" "%CTL%" running') do set "RUNNING=%%R"
if /I "%RUNNING%"=="yes" (
  echo [1/3] 실행 중인 서버 종료...
  "%PY%" "%CTL%" kill >nul
  echo [2/3] 포트 해제 대기...
  "%PY%" "%CTL%" wait
) else (
  echo [1/3] 실행 중인 서버 없음
  echo [2/3] 건너뜀
)

echo [3/3] 서버 시작...
start "예배 준비실 서버" /D "%ROOT%" "%PY%" start.py

echo.
echo 재시작 요청을 보냈습니다.
echo 브라우저: http://127.0.0.1:%PORT%
echo.
timeout /t 3 /nobreak >nul
