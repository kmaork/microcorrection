from http import HTTPStatus
from typing import Dict

from flask import Blueprint, jsonify, request, render_template, current_app, abort

from ..utils import get_level_data, set_level, get_rom, get_level, is_level_allowed, allow_level, signed_serializer
from ..db import emulator_sess, get_emulator, get_dbg_emulator
from ..emulator import Emulator, DebuggedEmulator

cpu = Blueprint('cpu', __name__)


@cpu.route('/is_alive', methods=['POST'])
def is_alive():
    return jsonify(emulator_sess.exists())


# TODO: this is used only by tests
@cpu.route('/set_level/<level>', methods=['POST'])
def set_level_view(level):
    if is_level_allowed(level):
        set_level(level)
    else:
        abort(HTTPStatus.UNAUTHORIZED)
    return jsonify()


def debugger():
    disassembly = get_level_data('disassembly.html').read_text()
    return render_template('debugger.html.jinja2', disassembly=disassembly, level=get_level())


@cpu.route('/debugger/<level>')
def debugger_specific_level(level: str):
    token = request.args.get('t')
    if token:
        token_level = signed_serializer.loads(token.encode())
        if token_level != level:
            abort(400)
        allow_level(token_level)
    set_level_view(level)
    return debugger()


@cpu.route('/load', methods=['POST'])
def load():
    emu = emulator_sess.get()
    is_debug = emu is not None and emu.IS_DEBUGGED
    return jsonify(data=dict(isdebug=is_debug, reason='', state='0'))


def start_emulator(debug):
    emu_cls = DebuggedEmulator if debug else Emulator
    old_emu = emulator_sess.get()
    new_emu = emu_cls.run(get_rom())
    if isinstance(old_emu, DebuggedEmulator) and isinstance(new_emu, DebuggedEmulator):
        breakpoints = old_emu.get_breakpoint_addrs()
        for breakpoint_addr in breakpoints:
            new_emu.set_breakpoint(breakpoint_addr)
    emulator_sess.store(new_emu)
    return jsonify(data=dict(success=True))


@cpu.route('/reset/debug', methods=['POST'])
def debug():
    return start_emulator(True)


@cpu.route('/reset/nodebug', methods=['POST'])
def nodbg():
    return start_emulator(False)


def get_mem_str(update_memory_map: Dict[int, bytes]) -> str:
    return ''.join(f'{addr:04X}{bytes.hex()}' for addr, bytes in update_memory_map.items())


@cpu.route('/snapshot')
def get_snapshot():
    emu = get_emulator()
    snap = emu.get_snapshot()
    return jsonify(advanced=snap.advanced.value,
                   advanced_steps=snap.instructions,
                   insn=snap.pc,
                   disasm=snap.disasm.decode(),
                   insn_bytes=snap.insn_bytes.hex(),
                   isdebug=('false', 'true')[emu.IS_DEBUGGED],
                   new_output=snap.new_output.hex(),
                   reason=snap.stop_reason.value,
                   regs=snap.regs,
                   state=snap.state.value,
                   updatememory=get_mem_str(snap.update_memory))


@cpu.route('/send_input', methods=['POST'])
def send_input():
    hexs = request.get_json()['body']
    input_bytes = bytes.fromhex(hexs)
    emu = get_emulator()
    mode = 'debug' if emu.IS_DEBUGGED else 'solve'
    current_app.logger.info(f'{request.remote_addr} sent input {input_bytes} for level {get_level()} ({mode} mode)')
    emu.write_input_to_emulator(input_bytes)
    return jsonify(data=dict(success=True))


@cpu.route('/step', methods=['POST'])
def step():
    """
    Step and return when complete
    """
    get_dbg_emulator().step()
    return get_snapshot()


@cpu.route('/regs', methods=['POST'])
def set_reg():
    """
    Set a register's value
    """
    emu = get_dbg_emulator()
    reg_i = request.get_json()['reg']
    val = request.get_json()['val']
    emu.set_reg(reg_i, val)
    return jsonify(data=dict(regs=emu.get_regs()))


@cpu.route('/updatememory', methods=['POST'])
def set_mem():
    """
    Change memory at given address
    """
    emu = get_dbg_emulator()
    addr = int(request.get_json()['addr'])
    val = int(request.get_json()['val'])
    emu.set_mem(addr, val)
    updates = get_mem_str(emu.get_update_memory())
    emu.sent_memory_updates()
    return jsonify(updatememory=updates)
