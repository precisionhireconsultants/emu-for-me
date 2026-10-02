"""Windows physical-input detection; stores timestamps and held keys only."""
import sys
import threading
import time


def session_is_unlocked():
    """Query Windows session lock state explicitly (Windows 10/11)."""
    import ctypes
    from ctypes import wintypes
    class Level1(ctypes.Structure):
        _fields_ = [('session_id', wintypes.DWORD), ('state', ctypes.c_int),
                    ('flags', wintypes.LONG), ('station', wintypes.WCHAR * 33),
                    ('user', wintypes.WCHAR * 21), ('domain', wintypes.WCHAR * 18),
                    ('times', ctypes.c_longlong * 5), ('counts', wintypes.DWORD * 6)]
    class Info(ctypes.Structure):
        _fields_ = [('level', wintypes.DWORD), ('data', Level1)]
    api = ctypes.WinDLL('wtsapi32', use_last_error=True)
    api.WTSQuerySessionInformationW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
        ctypes.c_int, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(wintypes.DWORD)]
    api.WTSQuerySessionInformationW.restype = wintypes.BOOL
    api.WTSFreeMemory.argtypes = [ctypes.c_void_p]
    memory = ctypes.c_void_p()
    size = wintypes.DWORD()
    if not api.WTSQuerySessionInformationW(None, 0xFFFFFFFF, 25,
                                          ctypes.byref(memory), ctypes.byref(size)):
        return False
    try:
        if not memory.value or size.value < ctypes.sizeof(Info):
            return False
        info = ctypes.cast(memory, ctypes.POINTER(Info)).contents
        return info.level == 1 and info.data.state == 0 and info.data.flags == 1
    finally:
        api.WTSFreeMemory(memory)


def desktop_accepts_input():
    """False on the lock screen, secure desktop, or an unavailable desktop."""
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.GetCurrentThreadId.restype = wintypes.DWORD
    user32.GetThreadDesktop.argtypes = [wintypes.DWORD]
    user32.GetThreadDesktop.restype = wintypes.HANDLE
    user32.GetUserObjectInformationW.argtypes = [wintypes.HANDLE, ctypes.c_int,
        ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    user32.GetUserObjectInformationW.restype = wintypes.BOOL
    desktop = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
    receiving_input = wintypes.BOOL()
    needed = wintypes.DWORD()
    return bool(session_is_unlocked() and desktop and user32.GetUserObjectInformationW(desktop, 6,
        ctypes.byref(receiving_input), ctypes.sizeof(receiving_input),
        ctypes.byref(needed)) and receiving_input.value)


class UserActivity:
    def __init__(self, idle_seconds=30, clock=time.monotonic, desktop_probe=None):
        self.idle_seconds = idle_seconds
        self.clock = clock
        self.last_input = clock()  # Allow time to leave the launch terminal.
        self.held = set()
        self.lock = threading.Lock()
        self.listeners = []
        self.manual_paused = False
        self.hotkey_latched = False
        self.desktop_probe = desktop_probe
        self.desktop_available = True

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
        available = self.desktop_probe() if self.desktop_probe else True
        with self.lock:
            if not available:
                # Releases on the secure desktop may never reach our hooks.
                self.held.clear()
                self.hotkey_latched = False
            elif not self.desktop_available:
                self.last_input = self.clock()
            self.desktop_available = available
            return (not available or self.manual_paused or bool(self.held)
                    or self.clock() - self.last_input < self.idle_seconds)

    def keyboard_filter(self, message, data):
        self.record(bool(data.flags & 0x12), ('key', data.vkCode),
                    message in (0x100, 0x104))
        if not data.flags & 0x12:
            with self.lock:
                keys = {token[1] for token in self.held
                        if isinstance(token, tuple) and token[0] == 'key'}
                chord = (bool(keys & {0x11, 0xA2, 0xA3})
                         and bool(keys & {0x12, 0xA4, 0xA5})
                         and {0x53, 0x41} <= keys)
                if chord and not self.hotkey_latched:
                    self.manual_paused = not self.manual_paused
                self.hotkey_latched = chord
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
        if self.desktop_probe is None:
            self.desktop_probe = desktop_accepts_input
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
