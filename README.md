# Emu for Me

Adapted from Just A Human's article (December 12, 2025):
https://medium.com/@JustaH/emu-for-me-72a803d4a21f

This implementation retains randomized mouse movement, weighted typing,
scrolling, window switching, and activity/quiet periods. It adds validated
configuration, optional timed runs, dry-run mode, visible errors, and reliable
Alt-key release. No license was supplied by the article; this repository does
not claim a license for the original author's work.

## Windows

**Double-click `AAStart-Emu.bat`** to open a console that asks for minutes.
Enter a number (for example `60`) and press Enter, or press Enter with a blank
answer to run indefinitely. Invalid numbers are rejected and the prompt repeats.
Run `setup.bat` once before first use. The double-click launcher shows only the
minutes prompt during normal use and closes after completion. Errors remain
visible. All pause and stop controls still apply.

Run `setup.bat`, then `start_app.bat 5` for five minutes.
Setup stays open on both success and failure and saves diagnostics in
`setup.log`. If Python is missing, it displays installation instructions.
Setup explicitly tries Python 3.11, then 3.12, 3.13, and 3.14 through the
Windows Python launcher before checking its generic Python 3 choice and PATH.
This works even when your default Python is 3.8. Install 3.11 alongside 3.8
with the Python launcher included; no PATH or default-Python change is needed.
The chosen interpreter is used only to create this app's `.venv`.
Use `start_app.bat 60` for sixty minutes, or `start_app.bat` with no duration
to run indefinitely until you stop it. Minutes can be fractional, such as
`start_app.bat 0.5` for thirty seconds. Zero, negative, and nonfinite durations
are rejected. A specified duration includes paused/locked time and exits
automatically, even when the app is manually paused. All pause/resume,
shortcut, and lock-screen behavior is the same in both runtime modes.
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
folder on a Windows 10/11 x64 PC, then run `portable_start.bat` (indefinite
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

Mouse strokes follow gently curved paths with acceleration/deceleration,
varied distances and durations, and small intermediate variations. Typing uses
varied key-hold times, uneven gaps, and occasional longer pauses between keys.
These are naturalistic timing variations, not meaningful human-written text.
Typing remains disabled by default because characters modify the focused app.
All strokes stay on the current monitor and can be interrupted by real input;
simulated keys are released even if typing is interrupted.

## Automatic pause while you work (Windows)

Hold **Ctrl+Alt+S+A** together to toggle manual pause. Press the chord again
to enable resuming after the idle delay. Holding the chord or key repeat does
not toggle repeatedly. The shortcut is observed globally and is not suppressed,
so the foreground application can also receive it. It requires the default
`user_activity.enabled: true` setting and is unavailable in dry-run mode.

Locking Windows pauses simulation. Returning from the lock screen starts a
fresh idle delay before resuming. Manual pause stays in effect across a lock.
Secure desktops (such as UAC) and desktop-query failures also pause simulation.
Lock detection uses an explicit Windows session-lock query in addition to the
desktop check. Physical-input pause/resume, the shortcut, and actual lock/unlock
were manually verified on the development PC; see `TESTING.md` for evidence
and the acceptance checklist for a new PC.

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
and https://learn.microsoft.com/en-us/windows/win32/api/wtsapi32/ns-wtsapi32-wtsinfoex_level1_w

Run checks with `.venv\Scripts\python.exe -m unittest discover -s tests -v`.

Double-click `test_installation.bat` to run the full installation checks in
disposable folders with spaces in their names, controlled PATH, no copied
virtual environment, and no pip cache. This downloads fresh packages and
tests missing Python, incomplete extraction, unavailable packages, readable
failure logs, the default pause on failure, and a successful double-click launch.
GitHub runs these checks on fresh Windows runners with Python 3.11 and 3.14
on every push and pull request. These checks isolate files and Python packages;
they do not emulate every Windows policy, device, or operating-system edition.
