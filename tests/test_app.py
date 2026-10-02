import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from types import SimpleNamespace
from user_activity import UserActivity
import activity_app as app


class Checks(unittest.TestCase):
    def test_physical_input_pauses_and_idle_resumes(self):
        now = [0]
        monitor = UserActivity(30, clock=lambda: now[0])
        now[0] = 31
        self.assertFalse(monitor.busy())
        monitor.keyboard_filter(0x100, SimpleNamespace(flags=0, vkCode=65))
        self.assertTrue(monitor.busy())
        now[0] = 100
        self.assertTrue(monitor.busy())  # Held keys prevent resume.
        monitor.keyboard_filter(0x101, SimpleNamespace(flags=0, vkCode=65))
        now[0] = 129
        self.assertTrue(monitor.busy())
        now[0] = 130
        self.assertFalse(monitor.busy())

    def test_synthetic_input_does_not_delay_resume(self):
        now = [0]
        monitor = UserActivity(30, clock=lambda: now[0])
        now[0] = 31
        monitor.keyboard_filter(0x100, SimpleNamespace(flags=0x10, vkCode=65))
        monitor.mouse_filter(0x200, SimpleNamespace(flags=1))
        self.assertFalse(monitor.busy())

    def test_mouse_drag_prevents_resume(self):
        now = [0]
        monitor = UserActivity(30, clock=lambda: now[0])
        monitor.mouse_filter(0x201, SimpleNamespace(flags=0))
        now[0] = 100
        self.assertTrue(monitor.busy())
        monitor.mouse_filter(0x202, SimpleNamespace(flags=0))
        now[0] = 131
        self.assertFalse(monitor.busy())

    def test_busy_user_gets_no_simulated_input(self):
        backend = Mock()
        monitor = UserActivity(30)
        app.run(app.DEFAULT_CONFIG, .0005, backend, monitor=monitor)
        self.assertEqual(backend.mock_calls, [])

    def test_resume_after_user_finishes(self):
        config = self.load({'mouse': {'enabled': False}, 'scrolling': {
            'enabled': True, 'scroll_probability': 1}, 'activity': {
            'min_delay_seconds': .01, 'max_delay_seconds': .01}})
        backend = Mock()
        monitor = Mock()
        monitor.busy.side_effect = [True, False] + [False] * 10000
        with patch('builtins.print'):
            app.run(config, .001, backend, monitor=monitor)
        backend.scroll.assert_called()

    def test_typing_stops_mid_burst_when_user_returns(self):
        config = self.load({'mouse': {'enabled': False}, 'keyboard': {
            'enabled': True, 'key_press_probability': 1,
            'min_keys_per_burst': 4, 'max_keys_per_burst': 4}})
        monitor = UserActivity(0)
        backend = Mock()
        def user_returns(*args):
            monitor.idle_seconds = 30
            monitor.record()
        backend.press.side_effect = user_returns
        app.run(config, .001, backend, monitor=monitor)
        self.assertEqual(backend.press.call_count, 1)

    def load(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'
            path.write_text(json.dumps(data))
            return app.load_config(path)

    def test_defaults_are_not_mutated(self):
        self.load({'mouse': {'enabled': False}})
        self.assertTrue(app.DEFAULT_CONFIG['mouse']['enabled'])

    def test_reject_invalid_values(self):
        for data in [{'activity': {'min_delay_seconds': 9, 'max_delay_seconds': 2}},
                     {'keyboard': {'key_press_probability': 2}},
                     {'mouse': {'enabled': 'yes'}},
                     {'keyboard': {'max_keys_per_burst': 2.5}}]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.load(data)

    def test_dry_run_never_uses_backend(self):
        backend = Mock()
        app.run(app.DEFAULT_CONFIG, .0001, backend, dry_run=True)
        self.assertEqual(backend.mock_calls, [])

    def test_alt_released_after_error(self):
        config = self.load({'mouse': {'enabled': False},
                            'window_switching': {'enabled': True, 'min_interval_seconds': 0, 'max_interval_seconds': 0}})
        backend = Mock()
        backend.press.side_effect = RuntimeError('test')
        with self.assertRaises(RuntimeError):
            app.run(config, .01, backend)
        backend.keyUp.assert_called_once_with('alt')


if __name__ == '__main__':
    unittest.main()
