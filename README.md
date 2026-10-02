# Emu for Me

Adapted from Just A Human's article (December 12, 2025):
https://medium.com/@JustaH/emu-for-me-72a803d4a21f

This implementation retains randomized mouse movement, weighted typing,
scrolling, window switching, and activity/quiet periods. It adds validated
configuration, a bounded runtime, dry-run mode, visible errors, and reliable
Alt-key release. No license was supplied by the article; this repository does
not claim a license for the original author's work.

## Windows

Run `setup.bat`, then `start_app.bat 5` for five minutes.
Run `start_app.bat 0.1 --dry-run` to log planned actions without sending input.
Stop with Ctrl+C or close the console window. The mouse-corner failsafe is
checked during simulated mouse movement; moving there while already paused
does not guarantee an exit.

## Moving to a new PC

**Use `releases/EmuForMe-Windows-source.zip` for the tested installation route.**
Install Python 3.11+ on the new Windows PC, extract the ZIP, run `setup.bat`,
then `verify_pc.bat` and `start_app.bat`. Setup creates a fresh local environment.
The source launcher was tested with Python 3.14 on this PC; other versions and
machines still require the verification check. Python installation and initial
dependency download require internet access; normal use after setup does not.
Create an updated source ZIP with `python build_source.py`.

**Experimental native bundle:** the unsigned folder executable is currently
blocked on this PC by Windows Application Control (WinError 4551). Its final
packaged behavior is not validated; use the source route above. The information
below describes its intended deployment, rather than a verified release.

The experimental bundle is `releases/EmuForMe-Windows-x64.zip`. Extract the entire
folder on a Windows 10/11 x64 PC, then run `portable_start.bat` (five minutes
by default) or `EmuForMe.exe 60` from a console for sixty minutes. Python,
Git, this computer's D: drive, and administrator rights are not required.
Keep `config.json` and the `_internal` dependency folder next to the executable.
Copy the entire extracted folder, rather than the executable alone.
Do not copy `.venv` to another PC.
The bundle includes Python and its dependencies. macOS/Linux and native ARM64
are not supported by this release. Policy restrictions or security software
may prevent an unsigned executable or global input hooks from running.

For source installation, copy the repository without `.venv`, `build`, or
`dist`; install Python 3.11+ on Windows, then run `setup.bat` in the new folder.
The launcher supports both the Python launcher (`py`) and `python` on PATH.
Paths are resolved relative to the app, including paths with spaces. Mouse
movement uses the monitor currently containing the pointer and virtual desktop
coordinates, including monitors left of the primary screen. Display awareness
is initialized before input libraries are loaded.

Run `verify_pc.bat` on each new PC before a live run (source setup or bundle).
This observes real input
for three minutes without typing, scrolling, switching windows, or moving the
pointer. First wait for `paused=False`; then type or move the pointer and check
`paused=True`. Wait for the idle delay and check it becomes false again. Hold
Ctrl+Alt+S+A and check `manual_pause=True`; release and press it again to check
false. Lock with Win+L, unlock, then check `desktop_available=False` followed
by true and a new idle wait in the console output. Ctrl+C ends verification.
This manual hardware check is necessary because synthetic input is deliberately
ignored and cannot stand in for a physical keyboard or mouse.

Build a new portable release with `powershell -ExecutionPolicy Bypass -File
build_portable.ps1`. Build on Windows x64 using x64 Python. Automated process
tests launch the real app but do not physically lock the PC or press keys.

Only mouse movement is enabled by default. To enable other actions, edit
`config.json`. Typing changes the focused application; window switching and
scrolling also affect the desktop. Run with documents saved and use deliberate
configuration. The simulator does not click.

## Automatic pause while you work (Windows)

Hold **Ctrl+Alt+S+A** together to toggle manual pause. Press the chord again
to enable resuming after the idle delay. Holding the chord or key repeat does
not toggle repeatedly. The shortcut is observed globally and is not suppressed,
so the foreground application can also receive it. It requires the default
`user_activity.enabled: true` setting and is unavailable in dry-run mode.

Locking Windows pauses simulation. Returning from the lock screen starts a
fresh idle delay before resuming. Manual pause stays in effect across a lock.
Secure desktops (such as UAC) and desktop-query failures also pause simulation.

To quit completely, **press Ctrl+C in the app's console**, or **close that
console window**. The runtime limit also exits automatically. If necessary,
use Task Manager's Details tab to end the app's specific `python.exe` process;
do not end unrelated Python processes. No tray icon or settings window is used.

Physical keyboard input, pointer movement, mouse buttons, and scrolling pause
the simulation. It resumes after 30 seconds without physical input. Change
`user_activity.resume_after_idle_seconds` in `config.json` to adjust that delay.
Held keys and mouse buttons keep it paused. Launching also starts with the idle
wait, giving you time to leave the terminal. Paused time counts toward the
requested runtime; resuming starts a fresh activity burst.

The listeners retain only an activity timestamp and currently held key/button
identifiers in memory; they do not record typed text. Injected Windows input
is ignored. Remote-control and accessibility software may send injected input,
so those inputs may not trigger pausing. Detection is checked roughly every
20 milliseconds; an already-issued input event cannot be recalled. Alt is
released when a window-switch sequence is interrupted. Dry-run skips listeners.
Listener failure stops the app rather than allowing unmonitored simulation.

References: https://pynput.readthedocs.io/en/latest/faq.html and
https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-msllhookstruct

Run checks with `.venv\Scripts\python.exe -m unittest discover -s tests -v`.
