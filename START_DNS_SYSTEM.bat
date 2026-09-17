@echo off

title DNS Hijacking Detection System

cd /d "%~dp0"

:: Check if running as Administrator
fltmc >nul 2>&1

if not %errorlevel%==0 (
    echo Requesting Administrator privileges...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ============================================================
echo       DNS HIJACKING DETECTION AND AUTO-RECOVERY SYSTEM
echo ============================================================
echo.
echo Running with Administrator privileges.
echo.

call ".venv\Scripts\activate.bat"

python app.py

pause