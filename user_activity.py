"""Windows physical-input detection; stores timestamps and held keys only."""
import sys
import threading
import time


class UserActivity:
    def __init__(self, idle_seconds=30, clock=time.monotonic):
        self.idle_seconds = idle_seconds
        self.clock = clock
        self.last_input = clock()  # Allow time to leave the launch terminal.
        self.held = set()
        self.lock = threading.Lock()
        self.listeners = []

    def record(self, injected=False, token=None, down=None):
        if injected:
            return
        with self.lock:
            self.last_input = self.clock()
            if token is not None:
                if down:
                    self.held.add(token)
                else:
                    self.held.discard(token)

    def busy(self):
        with self.lock:
            return bool(self.held) or self.clock() - self.last_input < self.idle_seconds

    def keyboard_filter(self, message, data):
        self.record(bool(data.flags & 0x12), ('key', data.vkCode),
                    message in (0x100, 0x104))
        return True  # Never block the user's input.

    def mouse_filter(self, message, data):
        buttons = {0x201: ('left', True), 0x202: ('left', False),
                   0x204: ('right', True), 0x205: ('right', False),
                   0x207: ('middle', True), 0x208: ('middle', False)}
        token, down = buttons.get(message, (None, None))
        if message in (0x20B, 0x20C):
            token, down = ('extra', data.mouseData >> 16), message == 0x20B
        self.record(bool(data.flags & 3), token, down)
        return True

    def __enter__(self):
        if sys.platform != 'win32':
            raise RuntimeError('Automatic user-input pausing currently requires Windows')
        from pynput import keyboard, mouse
        self.listeners = [keyboard.Listener(win32_event_filter=self.keyboard_filter),
                          mouse.Listener(win32_event_filter=self.mouse_filter)]
        try:
            for listener in self.listeners:
                listener.start()
                listener.wait()
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    def check(self):
        for listener in self.listeners:
            if not listener.is_alive():
                raise RuntimeError('Input listener stopped; stopping simulation')

    def __exit__(self, *args):
        for listener in self.listeners:
            listener.stop()
        for listener in self.listeners:
            listener.join(timeout=2)
