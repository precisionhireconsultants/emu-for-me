"""Real setup.bat tests in disposable folders with controlled environments."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRESH = os.environ.get('EMU_TEST_FRESH_INSTALL') == '1'


@unittest.skipUnless(os.name == 'nt', 'Windows batch installer')
class SetupChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='Emu isolated setup with spaces ')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        for name in ('setup.bat', 'requirements.txt', 'activity_app.py',
                     'user_activity.py', 'config.json', 'click_launcher.py', 'AAStart-Emu.bat'):
            shutil.copy2(ROOT / name, self.folder / name)
        self.env = dict(os.environ, PATH='', PYTHONNOUSERSITE='1', PIP_CONFIG_FILE=os.devnull,
                        PIP_DISABLE_PIP_VERSION_CHECK='1', PIP_NO_CACHE_DIR='1')
        for name in ('PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV', 'PIP_INDEX_URL',
                     'PIP_EXTRA_INDEX_URL', 'PIP_FIND_LINKS', 'PIP_NO_INDEX'):
            self.env.pop(name, None)

    def setup(self, pause=False, timeout=180):
        return subprocess.run([os.environ['COMSPEC'], '/d', '/c', 'setup.bat',
                               *([] if pause else ['--no-pause'])],
            cwd=self.folder, env=self.env, input='\n', text=True,
            capture_output=True, timeout=timeout)

    def enable_python(self):
        # Permit only the base interpreter, never this repo's virtual environment.
        self.env['PATH'] = str(Path(sys._base_executable).parent)

    def test_missing_python_is_visible_and_logged(self):
        result = self.setup()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('Python 3.11 or newer was not found', result.stdout)
        self.assertIn('Python 3.11 or newer was not found',
                      (self.folder / 'setup.log').read_text())
        self.assertFalse((self.folder / '.venv').exists())

    def test_double_click_failure_waits_for_user(self):
        result = self.setup(pause=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Press any key', result.stdout)
        self.assertIn('Setup failed', result.stdout)

    def test_incomplete_download_shows_missing_file(self):
        (self.folder / 'requirements.txt').unlink()
        result = self.setup()
        self.assertEqual(result.returncode, 1)
        self.assertIn('requirements.txt is missing', result.stdout)

    @unittest.skipUnless(FRESH, 'Set EMU_TEST_FRESH_INSTALL=1 for fresh dependency tests')
    def test_unavailable_packages_are_visible_and_logged(self):
        self.enable_python()
        self.env['PIP_NO_INDEX'] = '1'
        result = self.setup()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('Dependency installation failed', result.stdout)
        self.assertIn('Dependency installation failed',
                      (self.folder / 'setup.log').read_text())

    @unittest.skipUnless(FRESH, 'Set EMU_TEST_FRESH_INSTALL=1 for fresh dependency tests')
    def test_fresh_install_and_launcher_from_other_directory(self):
        self.enable_python()
        self.assertFalse((self.folder / '.venv').exists())
        result = self.setup()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Setup complete', result.stdout)
        python = self.folder / '.venv' / 'Scripts' / 'python.exe'
        self.assertTrue(python.exists())
        completed = subprocess.run([str(python), str(self.folder / 'activity_app.py'),
            '.005', '--dry-run'], cwd=ROOT.parent, env=self.env, text=True,
            capture_output=True, timeout=20)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('Runtime finished. Stopped.', completed.stdout)
        # Test the actual double-click batch wrapper without mouse or keyboard input.
        completed = subprocess.run([os.environ['COMSPEC'], '/d', '/c', 'AAStart-Emu.bat'],
            cwd=self.folder, env=self.env, input='.005\n\n', text=True,
            capture_output=True, timeout=20)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn('mons:', completed.stdout)
        self.assertIn('Runtime finished. Stopped.', completed.stdout)
