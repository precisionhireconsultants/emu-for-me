@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run setup.bat first.
    pause
    exit /b 1
)
set "EMU_TEST_FRESH_INSTALL=1"
".venv\Scripts\python.exe" -m unittest discover -s tests -p test_setup.py -v
set "taskTestExit=%errorlevel%"
pause
exit /b %taskTestExit%
