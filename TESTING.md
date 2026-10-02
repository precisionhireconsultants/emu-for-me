# Validation and remaining hardware checks

Passed source checks on the development Windows x64 PC, including a fresh
ZIP extraction and newly created Python environment: 20 tests passed. Five
optional native-bundle tests remain skipped after the execution-policy block.

- Configuration errors and independent defaults.
- Physical-event pause, held keys/buttons, and idle resume using controlled events.
- Four-key shortcut, key repeat, injected-event exclusion, and manual-pause persistence.
- Lock/unlock state transitions using a controlled desktop probe.
- Stopping a keyboard burst when user activity returns; releasing Alt on failure.
- Negative monitor coordinate normalization.
- Fresh CLI processes launched from an unrelated working directory.
- Native Windows listener startup, idle resume, and runtime expiry.
- Native mouse movement through the launched source app and launcher batch file.
- Fresh setup installation with pinned runtime dependencies, independent of D:.
- Forced source-process exit and verification-mode startup without simulated input.

The initial single-file executable also passed dry-run, adjacent-config,
native-mouse, and verification-mode checks in a relocated folder without Python
on PATH; it failed forced exit. The final native executable tests were blocked by Windows
Application Control (WinError 4551), so native packaging is experimental, not
a passed portability check. Run its tests explicitly with `EMU_TEST_PORTABLE=1`
only on a machine whose existing policy permits that executable. Default tests
skip that optional bundle suite. No security-policy change is needed for the
source installation route.

The first single-file packaging attempt failed the forced-exit check because
its bootstrap process left the application child running. The shipped release
was changed to a folder bundle to avoid that extra process. Forced exit of the
rebuilt bundle remains unverified because Windows blocked its execution.

These checks do not prove compatibility with every PC. Actual physical input,
four-key keyboard rollover, real lock/unlock, display scaling, multiple-monitor
layouts, and local security policy need verification on the target machine.
Synthetic input is deliberately ignored and cannot validate physical input.
The current release targets Windows x64. It has not been tested on another PC.

## Hardware acceptance checklist

1. Extract the source ZIP, install Python, run `setup.bat`, then `verify_pc.bat`.
2. Wait for `paused=False` (30 seconds by default).
3. Move the physical mouse, type, click, drag, and scroll. Verify it pauses for
   every action, stays paused while a key/button is held, then resumes after idle.
4. Hold Ctrl+Alt+S+A: verify `manual_pause=True`. Release it and wait more than
   30 seconds: it must remain paused. Press and release the chord again: verify
   `manual_pause=False`, followed by resume after the idle delay.
5. Lock with Win+L, wait several seconds, unlock, and inspect the console output:
   `desktop_available=False` must precede true, with a fresh idle delay.
6. Stop verification with Ctrl+C. Run `start_app.bat` for a live mouse-only
   run. Repeat input and shortcut checks, confirming movement stops as you work.
7. Repeat with the pointer on each monitor and with your normal scaling settings.
8. Exit with Ctrl+C and confirm the app's Python process is gone. Repeat
   with closing the console window.

No tray icon or settings window is needed for these checks.
