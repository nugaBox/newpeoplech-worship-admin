@echo off
setlocal EnableExtensions
chcp 65001 >nul
call "%~dp0_env.bat" || exit /b 1

echo.
echo ========================================
echo   예배 준비실 — 관리자 비밀번호 초기화
echo ========================================
echo.
echo DB에 저장된 관리자 비밀번호를 삭제하고
echo 로그인 세션도 모두 끊습니다.
echo.
set /p CONFIRM=정말 초기화하시겠습니까? (Y/N): 
if /I not "%CONFIRM%"=="Y" if /I not "%CONFIRM%"=="y" (
  echo 취소했습니다.
  pause
  exit /b 0
)

echo.
"%PY%" "%CTL%" admin-reset
echo.
pause
