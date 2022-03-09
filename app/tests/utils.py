import time
from contextlib import contextmanager
from http import HTTPStatus
from typing import Dict
from microserver.emulator.snapshot import State
from flask.testing import FlaskClient

from .levels import Level

NORMAL_SUCCESS = dict(data=dict(success=True))


def get(client: FlaskClient, url: str, expected_json=None, expected_status=HTTPStatus.OK):
    result = client.get(url)
    assert result.status_code == expected_status, f'Expected {expected_status}, got {result.status_code}'
    if expected_json is not None:
        assert result.json == expected_json, f'Expected {expected_json}, got {result.json}'
    return result


def post(client: FlaskClient, url: str, json=None, expected_json=None, expected_status=HTTPStatus.OK) -> dict:
    result = client.post(url, json=json)
    assert result.status_code == expected_status, f'Expected {expected_status}, got {result.status_code}'
    if expected_json is not None:
        assert result.json == expected_json, f'Expected {expected_json}, got {result.json}'
    return result.json


def set_level(client: FlaskClient, level: Level):
    post(client, f'/cpu/set_level/{level.name}', expected_json={})


def debug(client: FlaskClient):
    post(client, '/cpu/reset/debug', dict(body={}), NORMAL_SUCCESS)


def nodebug(client: FlaskClient):
    post(client, '/cpu/reset/nodebug', dict(body={}), NORMAL_SUCCESS)


def kill(client: FlaskClient):
    post(client, '/cpu/dbg/kill', dict(body={}))


@contextmanager
def debugger(client, level: Level):
    set_level(client, level)
    debug(client)
    try:
        yield
    finally:
        kill(client)


@contextmanager
def emulator(client, level: Level):
    set_level(client, level)
    nodebug(client)
    try:
        yield
    finally:
        kill(client)


def get_pc(snap):
    return snap['regs'][0]


def get_snap(client: FlaskClient):
    return get(client, '/cpu/snapshot').json


def parse_update_memory_str(s: str) -> Dict[int, bytes]:
    b = bytes.fromhex(s)
    return {int.from_bytes(b[i:i + 2], 'big'): b[i + 2:i + 18] for i in range(0, len(b), 18)}


def wait(client: FlaskClient):
    memory_updates = {}
    output = b''
    while True:
        time.sleep(0.05)
        snap = get_snap(client)
        memory_updates.update(parse_update_memory_str(snap['updatememory']))
        output += bytes.fromhex(snap['new_output'])
        if snap['state'] != State.WORKING.value:
            return snap, memory_updates, output


def cont(client: FlaskClient):
    post(client, '/cpu/dbg/continue', dict(body={}), NORMAL_SUCCESS)
    return wait(client)


def send_input(client: FlaskClient, s: str = ''):
    post(client, '/cpu/send_input', dict(body=s), NORMAL_SUCCESS)


def step_out(client: FlaskClient):
    post(client, '/cpu/dbg/step_out', dict(body=dict()), NORMAL_SUCCESS)
    return wait(client)


def step_over(client: FlaskClient):
    post(client, '/cpu/dbg/step_over', dict(body=dict()), NORMAL_SUCCESS)
    return wait(client)


def stepn(client: FlaskClient, step_n: int):
    post(client, f'/cpu/dbg/stepn/{step_n:x}', dict(body=dict()), NORMAL_SUCCESS)
    return wait(client)


def set_breakpoint(client: FlaskClient, addr: int):
    post(client, '/cpu/dbg/event', dict(body=dict(data=dict(addr=f'{addr:x}', event=0))), NORMAL_SUCCESS)


def delete_breakpoint(client: FlaskClient, addr: int):
    post(client, '/cpu/dbg/event', dict(body=dict(data=dict(addr=f'{addr:x}', event=-1))), NORMAL_SUCCESS)


def set_reg(client: FlaskClient, reg_i: int, reg_val: int) -> dict:
    return post(client, '/cpu/regs', dict(reg=reg_i, val=reg_val))


def set_mem(client: FlaskClient, addr: int, val: int) -> dict:
    return post(client, '/cpu/updatememory', dict(addr=addr, val=val))


def get_mem(client: FlaskClient, addr: int, length: int):
    return get(client, f'/cpu/dbg/memory/{addr:04x}?len={length}').json
