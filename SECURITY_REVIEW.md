# Security review — October 2, 2026

## Scope and results

Reviewed the application, launchers, installer, Windows input hooks, native API
calls, configuration parsing, and pinned Python dependencies.

- No application code for network connections, telemetry, uploads, remote
  commands, persistence, services, privilege elevation, or typed-text logging.
- Minutes are parsed as finite positive numbers; user-entered minutes are not
  interpolated into a shell command. Configuration is parsed as JSON, not code.
- Listeners track the latest physical activity time and currently held keys/
  buttons in memory. Typed text is not recorded or uploaded.
- Python socket operations were prohibited in launched-process tests of actual
  runtime startup and verification; both completed without attempting them.
  This is not a packet capture and does not cover every possible native or OS
  network operation or all duration/feature combinations.
- pip-audit 2.10.1 reported no known vulnerabilities in the 10 pinned runtime
  packages. The installed environment initially contained vulnerable pip 25.3.
  Upgrading it to 26.2.1 produced an environment audit with no known findings.

## Fix applied

Setup upgrades the app's local pip to 26.2.1 before installing runtime packages
and stops with a visible error if the upgrade cannot complete. It does not
upgrade the machine's default Python or its global pip. Existing installations
need to rerun the updated setup.bat to receive this installer fix.

## Practical limits

- Enabling typing sends characters to the currently focused application and
  can modify documents or interact with shortcuts. It remains off by default.
  An already-issued input event cannot be recalled when the user returns.
- Turning off `user_activity.enabled` also disables automatic listener-based
  pausing, the shortcut, and lock detection; the shipped configuration enables it.
- Remote-control/accessibility software can produce injected input that the
  physical-input detector deliberately ignores.
- Source files and the local environment must be trusted. Someone who can
  modify those files can execute code with the user's privileges. Run without
  administrator rights and keep the app in a folder other users cannot modify.
- Setup downloads Python packages and executes package installation/build
  tooling. Versions are pinned, but package artifact hashes are not enforced.
  Inherited pip configuration may select a different package index; use a
  trusted source. The review does not establish that every third-party package
  is free of undiscovered bugs or malicious code.
- Python itself, Windows, and other applications are outside this review.
  Keep the app's Python 3.11+ installation patched. This review does not audit
  the user's separate Python 3.8 installation.

Audit JSON files are saved locally under releases/; they are not runtime
dependencies or bundled telemetry. The audit tool was installed in a separate
review environment and is not included in the app's runtime requirements.

Tool reference: https://github.com/pypa/pip-audit
