"""Console prompt for the double-click launcher."""
import math
import os
from contextlib import redirect_stdout
from activity_app import main as run_app


def ask_minutes():
    while True:
        value = input('mons: ').strip()
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
    try:
        minutes = ask_minutes()
    except (KeyboardInterrupt, EOFError):
        print('\nCancelled.')
        return
    with open(os.devnull, 'w') as output, redirect_stdout(output):
        run_app([] if minutes is None else [str(minutes)])


if __name__ == '__main__':
    main()
