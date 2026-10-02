import unittest
from unittest.mock import patch
import click_launcher


class ClickLauncherChecks(unittest.TestCase):
    def test_blank_starts_indefinite_run(self):
        with patch('builtins.input', return_value=' '), patch.object(click_launcher, 'run_app') as run:
            click_launcher.main()
        run.assert_called_once_with([])

    def test_minutes_start_timed_run(self):
        with patch('builtins.input', return_value='12.5'), patch.object(click_launcher, 'run_app') as run:
            click_launcher.main()
        run.assert_called_once_with(['12.5'])

    def test_invalid_input_reprompts(self):
        with patch('builtins.input', side_effect=['0', '-1', 'nan', 'inf', 'bad & text', '5']):
            self.assertEqual(click_launcher.ask_minutes(), 5)

    def test_cancel_does_not_start_app(self):
        with patch('builtins.input', side_effect=KeyboardInterrupt), patch.object(click_launcher, 'run_app') as run:
            click_launcher.main()
        run.assert_not_called()
