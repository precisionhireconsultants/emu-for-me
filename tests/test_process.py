"""Launch the actual CLI in fresh child processes from another working folder."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProcessChecks(unittest.TestCase):
    def test_no_minutes_runs_until_terminated(self):
        process = subprocess.Popen([sys.executable, str(ROOT / 'activity_app.py'),
            '--dry-run'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertIn('Stop:', process.stdout.readline())
            self.assertIn('Runtime: indefinite', process.stdout.readline())
            self.assertIsNone(process.poll())
            process.terminate()
            process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=10)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows listeners')
    def test_timer_expires_even_while_paused(self):
        result = self.launch('.005')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Paused:', result.stdout)
        self.assertIn('Runtime finished. Stopped.', result.stdout)

    def launch(self, *args):
        with tempfile.TemporaryDirectory(prefix='emu process ') as directory:
            return subprocess.run([sys.executable, str(ROOT / 'activity_app.py'), *args],
                cwd=directory, capture_output=True, text=True, timeout=15)

    def test_launcher_uses_config_next_to_script(self):
        result = self.launch('.005', '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('mouse', result.stdout)

    def test_invalid_runtime_exits_with_error(self):
        result = self.launch('nan', '--dry-run')
        self.assertEqual(result.returncode, 2)
        self.assertIn('positive finite', result.stderr)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows listeners')
    def test_running_source_process_can_be_killed(self):
        process = subprocess.Popen([sys.executable, str(ROOT / 'activity_app.py'),
            '1', '--verify-input'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True)
        try:
            self.assertIn('Stop:', process.stdout.readline())
            process.terminate()
            process.communicate(timeout=10)
            self.assertIsNotNone(process.returncode)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=10)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows listeners')
    def test_native_listeners_start_idle_resume_and_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'config.json'
            config.write_text(json.dumps({'user_activity': {'resume_after_idle_seconds': .05},
                'mouse': {'enabled': False}, 'activity': {
                    'min_delay_seconds': .01, 'max_delay_seconds': .01}}))
            result = self.launch('.01', '--config', str(config))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Paused:', result.stdout)
        self.assertIn('Resuming:', result.stdout)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows listeners')
    def test_verification_mode_emits_status_without_generated_input(self):
        result = self.launch('.005', '--verify-input')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Verification only: no generated input', result.stdout)
        self.assertIn('manual_pause=False', result.stdout)


if __name__ == '__main__':
    unittest.main()
