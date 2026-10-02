@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" activity_app.py 3 --verify-input
) else if exist "EmuForMe.exe" (
    EmuForMe.exe 3 --verify-input
) else (
    echo Run setup.bat first.
)
pause
