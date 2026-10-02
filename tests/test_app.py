import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import activity_app as app


class Checks(unittest.TestCase):
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
