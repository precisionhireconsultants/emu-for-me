"""Check launched runtime startup with Python socket operations prohibited."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == 'win32', 'Windows input startup')
class SecurityChecks(unittest.TestCase):
    def test_live_startup_and_verification_do_not_attempt_socket_connections(self):
        code = '''
import sys
def deny_network(event, args):
    if event in ('socket.__new__', 'socket.connect', 'socket.getaddrinfo', 'socket.sendto'):
        raise RuntimeError('Network operation attempted: ' + event)
sys.addaudithook(deny_network)
import activity_app
activity_app.main(sys.argv[1:])
'''
        for extra in ([], ['--verify-input']):
            with self.subTest(extra=extra):
                result = subprocess.run([sys.executable, '-c', code, '.005', *extra],
                    cwd=ROOT, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('Runtime finished. Stopped.', result.stdout)
