from flask.testing import FlaskClient
from microserver.emulator.snapshot import State, Advance, Reason

from .levels import Level, new_orleans
from .utils import debugger, get_snap, cont, send_input, step_out, set_breakpoint, get_pc, delete_breakpoint, \
    set_reg, set_mem, step_over, get_mem, stepn


# TODO: add test for potential races
# TODO: stress tests

def test_prompt(client: FlaskClient, level: Level):
    with debugger(client, level):
        get_snap(client)  # get rid of initial mem updates
        snap, memory_updates, output = cont(client)
        assert snap['state'] == State.PROMPT.value
        assert snap['advanced'] == Advance.NOPE.value
        assert snap['isdebug'] == 'true'
        assert snap['reason'] == Reason.EMPTY.value
        assert snap['regs'] == level.first_cont_regs
        assert memory_updates == level.first_cont_mem_update
        assert output == level.first_cont_output


def test_initial_debugged_emulator_state_is_breakpoint(client: FlaskClient, example_level: Level):
    with debugger(client, example_level):
        state = get_snap(client)['state']
        assert state == State.BREAKPOINT.value


def test_step_out(client: FlaskClient):
    with debugger(client, new_orleans):
        cont(client)
        send_input(client)
        # in the original, the last one is 17528. this happens because we don't breakpoint on exit
        for expected_addr in [17806, 17594, 17486, 17486]:
            snap, _, _ = step_out(client)
            assert get_pc(snap) == expected_addr
        assert snap['state'] == State.STOPPED.value


def test_step_over(client: FlaskClient):
    start_addr = 0x4440
    next_addrs = [0x4444,  # 4 byte insn
                  0x4448,  # call
                  0x444a]  # 2 byte insn
    with debugger(client, new_orleans):
        set_breakpoint(client, start_addr)
        cont(client)
        for next_addr in next_addrs:
            snap, _, _ = step_over(client)
            assert get_pc(snap) == next_addr


def test_step_n(client: FlaskClient):
    n = 100
    with debugger(client, new_orleans):
        snap, _, _ = stepn(client, n)
        assert get_pc(snap) == 0x459a


def test_win(client: FlaskClient, level: Level):
    with debugger(client, level):
        snap, _, _ = cont(client)
        assert snap['state'] == State.PROMPT.value
        send_input(client, level.solution_hex)
        snap, memory_updates, output = cont(client)
        assert snap['state'] == State.STOPPED.value
        assert snap['advanced'] == Advance.DEBUG_WIN.value
        assert snap['isdebug'] == 'true'
        assert snap['reason'] == Reason.DEBUG_WIN_REASON.value
        assert output == level.win_output


def test_lose(client: FlaskClient, level: Level):
    with debugger(client, level):
        snap, _, _ = cont(client)
        assert snap['state'] == State.PROMPT.value
        send_input(client, '')
        snap, memory_updates, output = cont(client)
        assert snap['state'] == State.STOPPED.value
        assert snap['advanced'] == Advance.NOPE.value
        assert snap['isdebug'] == 'true'
        assert snap['reason'] == Reason.LOSE_REASON.value
        assert output == level.lose_output


def test_unaligned(client: FlaskClient, example_level: Level):
    with debugger(client, example_level):
        set_reg(client, 0, 0x4401)
        snap, memory_updates, output = cont(client)
        assert snap['state'] == State.STOPPED.value
        assert snap['advanced'] == Advance.NOPE.value
        assert snap['isdebug'] == 'true'
        assert snap['reason'] == Reason.UNALIGNED_REASON.value
        assert output == b''


def test_set_breakpoint(client: FlaskClient, example_level: Level):
    addr = 0x4408
    with debugger(client, example_level):
        set_breakpoint(client, addr)
        snap, _, _ = cont(client)
        assert get_pc(snap) == addr


def test_delete_breakpoint(client: FlaskClient):
    first_addr = 0x4408
    second_addr = 0x4414
    with debugger(client, new_orleans):
        set_breakpoint(client, first_addr)
        set_breakpoint(client, second_addr)
        delete_breakpoint(client, first_addr)
        snap, _, _ = cont(client)
        assert get_pc(snap) == second_addr


def test_set_reg(client: FlaskClient, example_level: Level):
    reg_i = 5
    reg_val = 0x49
    with debugger(client, example_level):
        result = set_reg(client, reg_i, reg_val)
        assert result['data']['regs'][reg_i] == reg_val
        snap = get_snap(client)
        assert snap['regs'][reg_i] == reg_val


def test_set_mem(client: FlaskClient):
    addr = 0x321
    val = 0x123
    with debugger(client, new_orleans):
        get_snap(client)  # get rid of initial memory update
        result = set_mem(client, addr, val)
        assert result['updatememory'] == '032000230100000000000000000000000000'
        snap = get_snap(client)
        assert snap['updatememory'] == ''


def test_get_mem(client: FlaskClient):
    addr = 0x4403
    length = 47
    expected_mem = 'RBVCXAF18zXQCFo/QAAAD5MHJIJFXAEvg59PwkUAJPkjP0AIAA+TBiSCRVwBH4M='
    with debugger(client, new_orleans):
        assert get_mem(client, addr, length) == dict(error=None, raw=expected_mem)
