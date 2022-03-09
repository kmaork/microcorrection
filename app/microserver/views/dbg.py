from enum import Enum
from flask import Blueprint, jsonify, request
from base64 import b64encode

from ..emulator import EmulatorStoppedException
from ..assembler import disassemble
from ..db import emulator_sess, get_emulator, get_dbg_emulator

dbg = Blueprint('dbg', __name__)
event_handlers = {}


class Event(Enum):
    SET_BREAKPOINT = 0
    DELETE_BREAKPOINT = -1


def event_handler(event: Event):
    def decorator(func):
        event_handlers[event.value] = func
        return func

    return decorator


@dbg.route('/events')
def get_events():
    emu = get_dbg_emulator()
    return jsonify(data=dict(events={f'{addr:04x}': 0 for addr in emu.get_breakpoint_addrs()}, success=True))


@dbg.route('/disasm')
def disassemble_get():
    try:
        opcodes = bytes.fromhex(request.args['obj'])
    except ValueError:
        output = ''
    else:
        output = disassemble(opcodes)
    return jsonify(data=dict(insns=output.split('\n')))


@dbg.route('/kill', methods=['POST'])
def kill():
    emulator_sess.remove()
    return ''


@dbg.route('/continue', methods=['POST'])
def cont():
    """
    Continue debugger and don't wait
    """
    get_emulator().cont()
    return jsonify(data=dict(success=True))


@dbg.route('/step_over', methods=['POST'])
def step_over():
    get_dbg_emulator().step_over()
    return jsonify(data=dict(success=True))


@dbg.route('/stepn/<step_n_hex>', methods=['POST'])
def step_n(step_n_hex: str):
    try:
        step_n = int(step_n_hex, 16)
    except ValueError:
        step_n = 1
    get_dbg_emulator().step_n(step_n)
    return jsonify(data=dict(success=True))


@dbg.route('/step_out', methods=['POST'])
def step_out():
    try:
        get_dbg_emulator().step_out()
    except EmulatorStoppedException:
        pass
    return jsonify(data=dict(success=True))


@event_handler(Event.SET_BREAKPOINT)
def set_breakpoint(event_data: dict):
    addr = int(event_data['addr'], 16)
    emu = get_dbg_emulator()
    if addr == emu.INTERRUPT_ADDR:
        # TODO: this should be an exception from the emulator class
        return dict(reason='Can not break at SWI address; only one breakpoint supported per address.', success=False)
    emu.set_breakpoint(addr)
    return dict(success=True)


@event_handler(Event.DELETE_BREAKPOINT)
def set_breakpoint(event_data: dict):
    addr = int(event_data['addr'], 16)
    emu = get_dbg_emulator()
    emu.delete_breakpoint(addr)
    return dict(success=True)


@dbg.route('/event', methods=['POST'])
def event():
    event_data = request.get_json()['body']['data']
    handler = event_handlers[event_data['event']]
    return jsonify(data=handler(event_data))


@dbg.route('/memory/<addr_hex>')
def get_mem(addr_hex):
    try:
        len = int(request.args['len'])
        addr = int(addr_hex, 16)
        emu = get_dbg_emulator()
    except Exception as e:
        return jsonify(error=str(e), raw='')
    return jsonify(error=None, raw=b64encode(emu.get_mem(addr, len)).decode())
