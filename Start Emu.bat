@echo off
title Emu for Me
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run setup.bat once before starting the app.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" click_launcher.py
pause
