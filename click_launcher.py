"""Console prompt for the double-click launcher."""
import math
from activity_app import main as run_app


def ask_minutes():
    while True:
        value = input('Minutes to run (leave blank for indefinite): ').strip()
        if not value:
            return None
        try:
            minutes = float(value)
            if math.isfinite(minutes) and minutes > 0:
                return minutes
        except ValueError:
            pass
        print('Enter a positive number of minutes, or leave blank.')


def main():
    print('Emu for Me')
    print('Ctrl+C stops the app. Ctrl+Alt+S+A toggles manual pause.\n')
    try:
        minutes = ask_minutes()
    except (KeyboardInterrupt, EOFError):
        print('\nCancelled.')
        return
    run_app([] if minutes is None else [str(minutes)])


if __name__ == '__main__':
    main()
