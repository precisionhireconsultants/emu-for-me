"""Integration checks for the ZIP release, independent of the source venv."""
import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parents[1] / 'releases' / 'EmuForMe-Windows-x64.zip'


@unittest.skipUnless(ARCHIVE.exists() and os.name == 'nt' and os.environ.get('EMU_TEST_PORTABLE') == '1',
                     'Opt-in unsigned bundle test; blocked here by Windows Application Control')
class PortableChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='Emu new PC path with spaces ')
        self.addCleanup(self.directory.cleanup)
        with zipfile.ZipFile(ARCHIVE) as archive:
            archive.extractall(self.directory.name)
        self.folder = Path(self.directory.name) / 'EmuForMe-Windows-x64'
        self.executable = self.folder / 'EmuForMe.exe'
        self.env = dict(os.environ, PATH='')
        for key in ('PYTHONHOME', 'PYTHONPATH', 'VIRTUAL_ENV'):
            self.env.pop(key, None)

    def launch(self, *args):
        return subprocess.run([str(self.executable), *args], cwd=self.directory.name,
            env=self.env, capture_output=True, text=True, timeout=20)

    def test_portable_dry_run_without_python_on_path(self):
        result = self.launch('.005', '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('mouse', result.stdout)

    def test_config_loaded_from_executable_folder(self):
        config = self.folder / 'config.json'
        config.write_text(json.dumps({'mouse': {'enabled': False}}))
        result = self.launch('.005', '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('\nmouse\n', result.stdout)

    def test_portable_native_mouse_run_and_idle_resume(self):
        config = self.folder / 'config.json'
        config.write_text(json.dumps({'user_activity': {'resume_after_idle_seconds': .1},
            'activity': {'min_delay_seconds': .1, 'max_delay_seconds': .1}}))
        result = self.launch('.02')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Resuming:', result.stdout)
        self.assertIn('\nmouse\n', result.stdout)

    def test_portable_verification_mode(self):
        result = self.launch('.005', '--verify-input')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('manual_pause=False', result.stdout)
        self.assertIn('desktop_available=True', result.stdout)

    def test_running_portable_process_can_be_killed(self):
        process = subprocess.Popen([str(self.executable), '1', '--verify-input'],
            cwd=self.directory.name, env=self.env, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True)
        try:
            self.assertIn('Stop:', process.stdout.readline())
            process.terminate()
            process.communicate(timeout=10)
            self.assertIsNotNone(process.returncode)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=10)


if __name__ == '__main__':
    unittest.main()
