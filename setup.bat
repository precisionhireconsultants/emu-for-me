@echo off
cd /d "%~dp0"
py -3 -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
if not errorlevel 1 (
    py -3 -m venv .venv
) else (
    python -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
    if errorlevel 1 (
        echo Python 3.11 or newer is required. Install Python or use the portable release.
        exit /b 1
    )
    python -m venv .venv
)
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip check
