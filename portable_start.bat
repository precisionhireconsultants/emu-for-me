@echo off
cd /d "%~dp0"
EmuForMe.exe %*
if errorlevel 1 pause
