@echo off
setlocal
title Emu setup
cd /d "%~dp0"
echo Installing Emu. Please wait...
echo Details are saved to setup.log in this folder.
call :install >setup.log 2>&1
set "taskSetupExit=%errorlevel%"
if "%taskSetupExit%"=="0" (
    echo Setup complete. You can now double-click AAStart-Emu.bat.
) else (
    echo.
    echo Setup failed. Details:
    type setup.log
    echo.
    echo Keep this window open to read the error, or open setup.log.
)
if /I not "%~1"=="--no-pause" pause
exit /b %taskSetupExit%

:install
if not exist "requirements.txt" (
    echo ERROR: requirements.txt is missing. Extract the entire app ZIP first.
    exit /b 1
)
py -3 -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
if not errorlevel 1 goto use_launcher
python -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
if not errorlevel 1 goto use_python
echo ERROR: Python 3.11 or newer was not found.
echo Install Python for Windows from https://www.python.org/downloads/windows/
echo Enable Add Python to PATH during installation, then run setup.bat again.
exit /b 1

:use_launcher
py -3 -m venv .venv
if errorlevel 1 goto venv_failed
goto dependencies

:use_python
python -m venv .venv
if errorlevel 1 goto venv_failed
goto dependencies

:venv_failed
echo ERROR: Unable to create the Python environment in this folder.
echo Check folder write access and that your Python installation includes venv.
exit /b 1

:dependencies
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed. See the pip error above.
    echo Check internet connectivity and any package-download restrictions.
    exit /b 1
)
".venv\Scripts\python.exe" -m pip check
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -c "import pyautogui, pynput"
if errorlevel 1 (
    echo ERROR: Input libraries could not be loaded. See the error above.
    exit /b 1
)
exit /b 0
