@echo off
rem 공용 환경 — setlocal 사용 금지 (호출한 bat에 변수 전달해야 함)

set "BIN=%~dp0"
for %%I in ("%BIN%..") do set "ROOT=%%~fI"
set "CTL=%BIN%_server.py"

set "PY=%ROOT%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

cd /d "%ROOT%"
if not exist "%CTL%" (
  echo [오류] bin\_server.py 를 찾을 수 없습니다.
  exit /b 1
)

for /f %%P in ('"%PY%" "%CTL%" port') do set "PORT=%%P"
if not defined PORT set "PORT=8000"

exit /b 0
