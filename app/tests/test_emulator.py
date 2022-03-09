from flask.testing import FlaskClient
from microserver.emulator.snapshot import State, Advance, Reason

from .utils import emulator, wait, send_input
from .levels import Level

UNKNOWN_REGS = [0] * 16


# TODO: test unaligned

def test_prompt(client: FlaskClient, level: Level):
    with emulator(client, level):
        snap, memory_updates, output = wait(client)
        assert snap['state'] == State.PROMPT.value
        assert snap['advanced'] == Advance.NOPE.value
        assert snap['isdebug'] == 'false'
        assert snap['reason'] == Reason.EMPTY.value
        assert snap['regs'] == UNKNOWN_REGS
        assert memory_updates == {}
        assert output == level.first_cont_output


# TODO: coddup with dbgemu tests
def test_win(client: FlaskClient, level: Level):
    with emulator(client, level):
        snap, _, _ = wait(client)
        assert snap['state'] == State.PROMPT.value
        send_input(client, level.solution_hex)
        snap, memory_updates, output = wait(client)
        assert snap['state'] == State.STOPPED.value
        assert snap['advanced'] == Advance.WIN.value
        assert snap['isdebug'] == 'false'
        assert snap['reason'] == Reason.REAL_WIN_REASON.value
        assert output == level.win_output


def test_lose(client: FlaskClient, level: Level):
    with emulator(client, level):
        snap, _, _ = wait(client)
        assert snap['state'] == State.PROMPT.value
        send_input(client, '')
        snap, memory_updates, output = wait(client)
        assert snap['state'] == State.STOPPED.value
        assert snap['advanced'] == Advance.NOPE.value
        assert snap['isdebug'] == 'false'
        assert snap['reason'] == Reason.LOSE_REASON.value
        assert output == level.lose_output
