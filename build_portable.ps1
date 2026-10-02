$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $taskPython)) { throw 'Run setup.bat first.' }
& $taskPython -c "import platform,struct,sys; sys.exit(0 if sys.platform == 'win32' and struct.calcsize('P') == 8 and platform.machine().lower() in ('amd64','x86_64') else 1)"
if ($LASTEXITCODE) { throw 'This release requires Windows x64 and x64 Python.' }
& $taskPython -m pip install -r requirements-build.txt
if ($LASTEXITCODE) { throw 'Build dependency installation failed.' }
& $taskPython -m PyInstaller --noconfirm --clean --onedir --console --name EmuForMe --hidden-import pynput.keyboard._win32 --hidden-import pynput.mouse._win32 activity_app.py
if ($LASTEXITCODE) { throw 'Executable build failed.' }
$taskRelease = Join-Path $PSScriptRoot 'releases\EmuForMe-Windows-x64'
New-Item -ItemType Directory -Force -Path $taskRelease | Out-Null
Get-ChildItem -LiteralPath 'dist\EmuForMe' | Copy-Item -Destination $taskRelease -Recurse -Force
Copy-Item -LiteralPath 'config.json','README.md','TESTING.md','portable_start.bat','verify_pc.bat' -Destination $taskRelease -Force
& $taskPython -c "import shutil; shutil.make_archive('releases/EmuForMe-Windows-x64', 'zip', 'releases', 'EmuForMe-Windows-x64')"
if ($LASTEXITCODE) { throw 'Release archive creation failed.' }
Write-Output "Portable release: $taskRelease"
