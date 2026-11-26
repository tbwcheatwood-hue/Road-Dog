@echo off
REM Road Dog — Dev-Launcher (Phase 1a)
REM Starts Frontend (Vite HMR) + Backend (FastAPI --dev) in parallel.
REM Window appears once both are healthy.

setlocal EnableDelayedExpansion
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 1) Frontend-Dev-Server in its own window.
REM    Port 5173 (Vite default). Expected in jarvis.toml ui.vite_dev_url.
pushd jarvis\ui\web\frontend
if not exist node_modules (
    echo [dev] node_modules missing — npm install...
    call npm install || goto :error
)
start "roaddog-vite" cmd /k npm run dev
popd

REM 2) Short buffer so Vite can bind before pywebview loads the URL.
timeout /t 2 /nobreak >nul

REM 3) Backend + window in foreground (Console output visible).
set JARVIS_DEV=1
set JARVIS_WEBVIEW_DEBUG=1
python -m jarvis.ui.web.launcher --dev %*

goto :end

:error
echo [dev] Abort — npm install failed.
exit /b 1

:end
endlocal
