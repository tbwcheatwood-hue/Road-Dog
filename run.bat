@echo off
REM Road Dog — Windows Launcher
REM Starts Road Dog in the user context (no admin required)

setlocal
cd /d "%~dp0"

REM Activate venv when present
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Pre-boot drift check: restore any tracked files that vanished from
REM the working tree. Always exits 0; never blocks boot. Skipped silently
REM when PowerShell is unavailable.
if exist "scripts\check-working-tree.ps1" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check-working-tree.ps1"
)

REM Start Road Dog desktop app (FastAPI + pywebview + React).
REM --debug → Console visible, --headless → backend only without window,
REM --dev → Frontend from Vite dev server (port 5173) instead of dist/.
if "%1"=="--debug" (
    REM --debug is batch-local: console visible + verbose logging.
    REM Forwarding it to the launcher would trip argparse.
    set JARVIS_DEBUG=1
    python -m jarvis.ui.web.launcher
) else if "%1"=="--headless" (
    python -m jarvis.ui.web.launcher --headless
) else if "%1"=="--dev" (
    set JARVIS_DEV=1
    python -m jarvis.ui.web.launcher --dev
) else (
    start "" pythonw -m jarvis.ui.web.launcher
)

endlocal
