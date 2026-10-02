"""Create a source ZIP without machine-specific environments or output files."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent
release = root / 'releases' / 'EmuForMe-Windows-source.zip'
release.parent.mkdir(exist_ok=True)
files = ['activity_app.py', 'user_activity.py', 'config.json', 'requirements.txt',
         'setup.bat', 'start_app.bat', 'verify_pc.bat', 'README.md', 'TESTING.md',
         'build_source.py', '.gitignore', 'click_launcher.py', 'AAStart-Emu.bat',
         'test_installation.bat']
with zipfile.ZipFile(release, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name in files:
        archive.write(root / name, 'EmuForMe/' + name)
    for path in (root / 'tests').glob('*.py'):
        archive.write(path, 'EmuForMe/tests/' + path.name)
print(release)
