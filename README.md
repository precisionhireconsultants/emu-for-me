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

Run checks with `.venv\Scripts\python.exe -m unittest discover -s tests -v`.
