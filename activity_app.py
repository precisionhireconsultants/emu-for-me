"""Desktop activity simulator adapted from Just A Human's Emu for Me article."""
import argparse
import copy
import json
import math
import random
import time
from contextlib import nullcontext
from pathlib import Path

DEFAULT_CONFIG = {
    'user_activity': {'enabled': True, 'resume_after_idle_seconds': 30},
    'activity': {'min_delay_seconds': 2, 'max_delay_seconds': 8,
                 'burst_duration_minutes': 3, 'quiet_duration_seconds': 60},
    'mouse': {'enabled': True},
    'keyboard': {'enabled': False, 'key_press_probability': .3,
                 'min_keys_per_burst': 1, 'max_keys_per_burst': 4},
    'window_switching': {'enabled': False, 'min_interval_seconds': 30,
                         'max_interval_seconds': 120, 'tabs_to_press': [1, 2, 3]},
    'scrolling': {'enabled': False, 'min_scroll_amount': 1,
                  'max_scroll_amount': 5, 'scroll_probability': .4},
}
KEYS = list('034589abcduvwxyz')
WEIGHTS = [1, .5, .5, .5, .5, .5, 8.2, 1.5, 2.8, 4.3, 2.8, 1, 2.4, .15, 2, .07]


def load_config(path):
    config = copy.deepcopy(DEFAULT_CONFIG)
    if path.exists():
        supplied = json.loads(path.read_text(encoding='utf-8'))
        for section, values in supplied.items():
            if section not in config or not isinstance(values, dict):
                raise ValueError(f'Invalid configuration section: {section}')
            for key, value in values.items():
                if key not in config[section]:
                    raise ValueError(f'Unknown setting: {section}.{key}')
                original = config[section][key]
                if isinstance(original, bool):
                    valid = isinstance(value, bool)
                elif isinstance(original, list):
                    valid = isinstance(value, list) and bool(value) and all(
                        type(item) is int and item > 0 for item in value)
                else:
                    valid = type(value) in (int, float) and math.isfinite(value) and value >= 0
                if not valid:
                    raise ValueError(f'Invalid value: {section}.{key}')
                config[section][key] = value
    for section, low, high in [
        ('activity', 'min_delay_seconds', 'max_delay_seconds'),
        ('keyboard', 'min_keys_per_burst', 'max_keys_per_burst'),
        ('window_switching', 'min_interval_seconds', 'max_interval_seconds'),
        ('scrolling', 'min_scroll_amount', 'max_scroll_amount')]:
        if config[section][low] > config[section][high]:
            raise ValueError(f'{section}: minimum exceeds maximum')
    for section, key in [('keyboard', 'key_press_probability'), ('scrolling', 'scroll_probability')]:
        if config[section][key] > 1:
            raise ValueError(f'{key} must be between 0 and 1')
    for section, keys in [('keyboard', ['min_keys_per_burst', 'max_keys_per_burst']),
                          ('scrolling', ['min_scroll_amount', 'max_scroll_amount'])]:
        if any(type(config[section][key]) is not int for key in keys):
            raise ValueError(f'{section}: counts must be integers')
    if config['activity']['burst_duration_minutes'] <= 0:
        raise ValueError('Burst duration must be positive')
    return config


def run(config, minutes, backend=None, dry_run=False, monitor=None):
    deadline = time.monotonic() + minutes * 60
    burst_end = time.monotonic() + config['activity']['burst_duration_minutes'] * 60
    switch = config['window_switching']
    next_switch = time.monotonic() + random.uniform(switch['min_interval_seconds'], switch['max_interval_seconds'])

    def pause(seconds):
        until = min(time.monotonic() + seconds, deadline)
        while time.monotonic() < until:
            if monitor:
                monitor.check()
                if monitor.busy():
                    break
            time.sleep(max(0, min(.02, until - time.monotonic())))

    def interrupted():
        return time.monotonic() >= deadline or (monitor is not None and monitor.busy())

    paused = False
    while time.monotonic() < deadline:
        if monitor:
            monitor.check()
            if monitor.busy():
                if not paused:
                    print('Paused: waiting for you to finish using the keyboard/mouse.', flush=True)
                paused = True
                time.sleep(min(.02, max(0, deadline - time.monotonic())))
                continue
            if paused:
                print('Resuming: idle period reached.', flush=True)
                burst_end = time.monotonic() + config['activity']['burst_duration_minutes'] * 60
                paused = False
        if time.monotonic() >= burst_end:
            pause(config['activity']['quiet_duration_seconds'])
            burst_end = time.monotonic() + config['activity']['burst_duration_minutes'] * 60
            continue
        choices = [name for name in ('mouse', 'keyboard', 'scrolling') if config[name]['enabled']]
        if switch['enabled'] and time.monotonic() >= next_switch:
            choices.append('window_switching')
        if not choices:
            pause(.1)
            continue
        action = random.choice(choices)
        print(action, flush=True)
        if action == 'window_switching':
            next_switch = time.monotonic() + random.uniform(switch['min_interval_seconds'], switch['max_interval_seconds'])
        if not dry_run:
            if interrupted():
                continue
            if action == 'mouse':
                width, height = backend.size()
                x, y = backend.position()
                angle = random.uniform(0, 2 * math.pi)
                distance = random.randint(100, 300)
                target_x = max(1, min(width - 2, x + distance * math.cos(angle)))
                target_y = max(1, min(height - 2, y + distance * math.sin(angle)))
                for step in range(1, 16):
                    if interrupted():
                        break
                    backend.failSafeCheck()
                    progress = backend.easeInOutCubic(step / 15)
                    # SetCursorPos is not marked as injected. Use synthetic
                    # Windows mouse events so our listener ignores our moves.
                    import ctypes
                    ctypes.windll.user32.mouse_event(0x8001,
                        int((x + (target_x - x) * progress) * 65535 / (width - 1)),
                        int((y + (target_y - y) * progress) * 65535 / (height - 1)), 0, 0)
                    pause(.02)
            elif action == 'keyboard' and random.random() < config[action]['key_press_probability']:
                for _ in range(random.randint(config[action]['min_keys_per_burst'], config[action]['max_keys_per_burst'])):
                    if interrupted():
                        break
                    backend.press(random.choices(KEYS, weights=WEIGHTS)[0])
                    pause(random.uniform(.2, .8))
            elif action == 'scrolling' and random.random() < config[action]['scroll_probability']:
                backend.scroll(random.choice([-1, 1]) * random.randint(config[action]['min_scroll_amount'], config[action]['max_scroll_amount']))
            elif action == 'window_switching':
                backend.keyDown('alt')
                try:
                    for _ in range(random.choice(switch['tabs_to_press'])):
                        if interrupted():
                            break
                        backend.press('tab')
                        pause(.15)
                finally:
                    backend.keyUp('alt')
        pause(random.uniform(config['activity']['min_delay_seconds'], config['activity']['max_delay_seconds']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('minutes', type=float, nargs='?', default=5)
    parser.add_argument('--config', type=Path, default=Path(__file__).with_name('config.json'))
    parser.add_argument('--dry-run', action='store_true', help='Log actions without desktop input')
    args = parser.parse_args()
    if not math.isfinite(args.minutes) or args.minutes <= 0:
        parser.error('minutes must be a positive finite number')
    try:
        config = load_config(args.config)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    backend = None
    if not args.dry_run:
        import pyautogui as backend
        backend.FAILSAFE = True
        backend.PAUSE = 0
    try:
        from user_activity import UserActivity
        settings = config['user_activity']
        context = UserActivity(settings['resume_after_idle_seconds']) if settings['enabled'] and not args.dry_run else nullcontext(None)
        with context as monitor:
            run(config, args.minutes, backend, args.dry_run, monitor)
    except KeyboardInterrupt:
        print('Stopped.')
    except Exception as exc:
        if backend and isinstance(exc, backend.FailSafeException):
            print('Stopped by mouse failsafe.')
        else:
            raise


if __name__ == '__main__':
    main()
