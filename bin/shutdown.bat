@echo off
setlocal EnableExtensions
chcp 65001 >nul
call "%~dp0_env.bat" || exit /b 1

echo.
echo ========================================
echo   예배 준비실 — 서버 중지
echo   포트: %PORT%
echo ========================================
echo.

for /f %%R in ('"%PY%" "%CTL%" running') do set "RUNNING=%%R"
if /I not "%RUNNING%"=="yes" (
  echo 서버가 실행 중이 아닙니다.
  echo.
  pause
  exit /b 0
)

"%PY%" "%CTL%" kill >nul
"%PY%" "%CTL%" wait
if errorlevel 1 (
  echo [경고] 포트 %PORT% 해제에 시간이 걸리고 있습니다.
) else (
  echo 서버를 중지했습니다.
)
echo.
pause
