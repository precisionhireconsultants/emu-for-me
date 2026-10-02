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
Stop with Ctrl+C or move the pointer to the top-left screen corner.

Only mouse movement is enabled by default. To enable other actions, edit
`config.json`. Typing changes the focused application; window switching and
scrolling also affect the desktop. Run with documents saved and use deliberate
configuration. The simulator does not click.

## Automatic pause while you work (Windows)

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
