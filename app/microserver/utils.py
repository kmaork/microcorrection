import os
from functools import wraps
from pathlib import Path
from threading import RLock
from typing import Any, Callable, List
from itsdangerous import URLSafeSerializer

import json
from flask import session, abort, url_for, redirect

SESSION_LEVEL = 'level'
SESSION_ALLOWED_LEVELS = 'allowed_levels'
NO_DEFAULT = object()
LEVEL_DIR = Path(__file__).parent / 'level_data'
DEFAULT_ALLOWED_LEVELS = ['Tutorial']
WITH_ADMIN = os.getenv('CORRUPT_WITH_ADMIN', '') == '1'
SECRET_KEY = 'This app should not be used in production anyway'

signed_serializer = URLSafeSerializer(SECRET_KEY)


def go_home():
    abort(redirect(url_for('home')))


def get_sess(name: str, default=NO_DEFAULT) -> Any:
    val = session.get(name)
    if not val:
        if default is NO_DEFAULT:
            go_home()
        val = default
    return val


def get_level() -> str:
    return get_sess(SESSION_LEVEL)


def set_level(level: str) -> None:
    session[SESSION_LEVEL] = level


def get_level_data(filename: str) -> Path:
    return LEVEL_DIR / get_level() / Path(filename).name


def get_levels_dict(only_allowed=False) -> dict:
    with open(Path(__file__).parent / 'views' / 'levels.json', 'rb') as f:
        levels_dict = json.load(f)
        if only_allowed:
            levels_dict['levels'] = [level for level in levels_dict['levels'] if is_level_allowed(level['name'])]
        return levels_dict


def get_level_names() -> List[str]:
    levels = []
    for level in get_levels_dict()['levels']:
        levels.append(level['name'])
    return levels


def allow_level(level_name: str):
    session.permanent = True
    allowed_levels = session.get(SESSION_ALLOWED_LEVELS, [])
    if level_name not in allowed_levels:
        allowed_levels.append(level_name)
    session[SESSION_ALLOWED_LEVELS] = allowed_levels


def is_level_allowed(level_name: str):
    return (not WITH_ADMIN) or level_name in (session.get(SESSION_ALLOWED_LEVELS, []) + DEFAULT_ALLOWED_LEVELS)


def get_rom() -> Path:
    return get_level_data('rom.bin')


class ThreadSafe:
    def __init__(self):
        self.lock = RLock()


def thread_safe(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)

    return wrapper
