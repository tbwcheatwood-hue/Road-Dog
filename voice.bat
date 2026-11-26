@echo off
REM Road Dog — Voice Pipeline Launcher
REM Starts the Speech Watchdog (Wake Word + STT + Brain + TTS).
REM
REM Usage:
REM   voice          → Default: Console visible, full logs in data/roaddog_watchdog.log
REM   voice --quiet  → Background (pythonw), no Console window
REM   voice --stop   → Stop all running Voice Watchdogs

setlocal EnableDelayedExpansion
cd /d "%~dp0"
set PIDFILE=data\roaddog_watchdog.pid

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

if "%1"=="--stop" goto :do_stop
if not exist "%PIDFILE%" goto :do_start
goto :check_running

:do_stop
REM Fast stop via PID file — no PowerShell, no process scan.
if not exist "%PIDFILE%" goto :stop_none
set /p WATCHDOG_PID=<"%PIDFILE%"
if "!WATCHDOG_PID!"=="" goto :stop_empty
tasklist /FI "PID eq !WATCHDOG_PID!" 2>NUL | find "!WATCHDOG_PID!" >NUL
if errorlevel 1 goto :stop_stale
REM PID is alive — verify it is really our watchdog (PID reuse guard).
python -c "import sys; from jarvis.speech.watchdog import recorded_watchdog_alive; sys.exit(0 if recorded_watchdog_alive() else 1)" >NUL 2>&1
if errorlevel 1 goto :stop_foreign
echo Stopping PID !WATCHDOG_PID!
taskkill /PID !WATCHDOG_PID! /F
del "%PIDFILE%" 2>NUL
goto :end
:stop_none
echo Voice-Watchdog is not running (no PID file).
goto :end
:stop_empty
del "%PIDFILE%" 2>NUL
echo Voice-Watchdog is not running (empty PID file cleaned up).
goto :end
:stop_stale
echo No running process at PID !WATCHDOG_PID! — cleaning up stale PID file.
del "%PIDFILE%" 2>NUL
goto :end
:stop_foreign
echo PID !WATCHDOG_PID! is not a Voice-Watchdog — cleaning up stale PID file (process NOT terminated).
del "%PIDFILE%" 2>NUL
goto :end

:check_running
REM Fast single-instance check: no PID file = instant start, straight to STT.
REM Only when a PID file exists do we spend one tasklist probe (~50ms) plus
REM one light python verify (~250ms) — still far below the old PowerShell
REM Get-CimInstance scan (~1s+). No permission hop anywhere on this path.
set /p WATCHDOG_PID=<"%PIDFILE%"
if "!WATCHDOG_PID!"=="" goto :stale_pid
tasklist /FI "PID eq !WATCHDOG_PID!" 2>NUL | find "!WATCHDOG_PID!" >NUL
if errorlevel 1 goto :stale_pid
python -c "import sys; from jarvis.speech.watchdog import recorded_watchdog_alive; sys.exit(0 if recorded_watchdog_alive() else 1)" >NUL 2>&1
if not errorlevel 1 goto :already_running
:stale_pid
del "%PIDFILE%" 2>NUL
goto :do_start
:already_running
echo Voice-Watchdog is already running (PID !WATCHDOG_PID!). Stop with: voice --stop
goto :end

:do_start

if "%1"=="--quiet" (
    REM Headless: pythonw opens no Console, logs go to data/roaddog_watchdog.log
    start "" pythonw -m jarvis.speech.watchdog
    echo Voice-Watchdog started in background.
    echo Logs: data\roaddog_watchdog.log
) else (
    REM Default: Console stays open — you see live logs.
    echo ================================================================
    echo   Voice-Watchdog starting. Stop with Ctrl+C or 'voice --stop'.
    echo   Logs stream to Terminal + data\roaddog_watchdog.log
    echo ================================================================
    python -m jarvis.speech.watchdog
)

:end
endlocal
