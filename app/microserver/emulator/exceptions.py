from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .debugger_commands import ParsableDbgCommand


@dataclass
class EmulatorException(Exception):
    reason: str

    def __str__(self):
        return self.reason


class DebuggedEmulatorException(EmulatorException):
    pass


class EmulatorStoppedException(DebuggedEmulatorException):
    pass


class DebuggerCommandException(DebuggedEmulatorException):
    pass


class DbgCommandOutputParsingException(DebuggerCommandException):
    def __init__(self, dbg_command: 'ParsableDbgCommand', output: bytes):
        super().__init__(f'The command "{dbg_command.cmd.decode()}" produced the output "{output.decode()}" '
                         f'that did not match the expected pattern "{dbg_command.pattern}"')
