@echo off
title Timer
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run setup.bat once before starting the app.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" click_launcher.py
if errorlevel 1 pause
