from typing import cast
from flask import abort

from .session_storage import SessionStorage
from .emulator import Emulator, DebuggedEmulator
from .utils import go_home

emulator_sess = SessionStorage('emulator')


def get_emulator() -> Emulator:
    emu = emulator_sess.get()
    if emu is None:
        go_home()
    return cast(Emulator, emu)


def get_dbg_emulator() -> DebuggedEmulator:
    emu = get_emulator()
    if isinstance(emu, DebuggedEmulator):
        return emu
    abort(400)
