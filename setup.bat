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
for %%V in (3.11 3.12 3.13 3.14) do (
    call py -%%V -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
    if not errorlevel 1 (
        set "taskPythonTag=-%%V"
        goto use_launcher
    )
)
set "taskPythonTag=-3"
call py -3 -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
if not errorlevel 1 goto use_launcher
call python -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
if not errorlevel 1 goto use_python
echo ERROR: Python 3.11 or newer was not found.
echo Install Python for Windows from https://www.python.org/downloads/windows/
echo Include the Python launcher. You can leave your Python 3.8 PATH unchanged.
echo Then run setup.bat again. Setup selects the newer version just for this app.
exit /b 1

:use_launcher
echo Using Python launcher version %taskPythonTag% for this app.
call py %taskPythonTag% -m venv .venv
if errorlevel 1 goto venv_failed
goto dependencies

:use_python
call python -m venv .venv
if errorlevel 1 goto venv_failed
goto dependencies

:venv_failed
echo ERROR: Unable to create the Python environment in this folder.
echo Check folder write access and that your Python installation includes venv.
exit /b 1

:dependencies
".venv\Scripts\python.exe" -m pip install --upgrade pip==26.2.1
if errorlevel 1 (
    echo ERROR: Installer upgrade failed. See the pip error above.
    exit /b 1
)
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
