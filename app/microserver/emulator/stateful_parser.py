import re
import time
from abc import ABC
from io import BytesIO
from typing import Any, TYPE_CHECKING

from .snapshot import State, Advance, Reason
from .utils import DontOverride

if TYPE_CHECKING:
    from .emulator import Emulator
    from .debugged_emulator import DebuggedEmulator


class StatefulParser(ABC):
    def __init__(self, input: BytesIO, emulator: 'Emulator') -> None:
        self.input = input
        self.emulator = emulator

    def _initialize(self):
        self.value = self.INITIAL_VALUE

    def _get_buffer(self) -> bytes:
        return self.input.getvalue()

    def _clear(self, new_data: bytes = None, start: int = 0) -> None:
        self.input.seek(start)
        self.input.truncate()
        if new_data:
            self.input.write(new_data)

    def _clear_lines(self) -> bytes:
        """
        Clear all lines from the input buffer except for the last one.
        This is useful when looking for single-line stuff while parsing.
        """
        buffer = self._get_buffer()
        last_line_start = buffer.rfind(b'\n') + 1
        lines = buffer[:last_line_start]
        self._clear(buffer[last_line_start:])
        return lines

    def _read_and_process_new_data(self) -> None:
        self._clear()


class SingleValueStatefulParser(StatefulParser):
    """
    A parser for a stream that has a value, that might change while parsing.
    To define the parser's behavior one can override the _read_new_data and _get_value methods.
    """

    INITIAL_VALUE: Any

    def __init__(self, input: BytesIO, emulator: 'Emulator') -> None:
        super().__init__(input, emulator)
        self.value = self.INITIAL_VALUE

    def __init_subclass__(cls, **kwargs) -> None:
        cls.INITIAL_VALUE = kwargs.pop('initial_value')

    def _get_value(self) -> Any:
        return self.value

    def get_value(self):
        if not self.input.closed:
            self._read_and_process_new_data()
        return self._get_value()


class CPUStateParser(SingleValueStatefulParser, initial_value=State.WORKING):
    def _read_and_process_new_data(self) -> None:
        if self.value == State.WORKING:
            if self._get_buffer().endswith(self.emulator.PROMPT_STR):
                self.value = State.PROMPT
                self._clear()
                return
        self._clear_lines()

    @DontOverride
    def _get_value(self) -> State:
        """ Overriding to change the type annotation """

    def input_was_provided(self):
        self.value = State.WORKING


class LevelAdvanceParser(SingleValueStatefulParser, initial_value=Advance.NOPE):
    def _read_and_process_new_data(self) -> None:
        if self.emulator.WIN_STR in self._get_buffer():
            self.value = Advance.DEBUG_WIN if self.emulator.IS_DEBUGGED else Advance.WIN
            # Don't clear so it will stay winning
        else:
            self._clear_lines()

    @DontOverride
    def _get_value(self) -> Advance:
        """ Overriding to change the type annotation """


class InstructionAmountParser(SingleValueStatefulParser, initial_value=0):
    def _read_and_process_new_data(self) -> None:
        match = re.search(self.emulator.INSTRUCTIONS_REGEX, self._get_buffer())
        if match is not None:
            self.value = int(match.group(1))
        else:
            self._clear_lines()

    @DontOverride
    def _get_value(self) -> int:
        """ Overriding to change the type annotation """


class UserOutputParser(SingleValueStatefulParser, initial_value=b''):
    def _read_and_process_new_data(self):
        lines = self._clear_lines()
        for regex in self.emulator.REMOVE_OUTPUT_REGEXES:
            lines = re.sub(regex, b'', lines)
        self.value += lines

    def sent_new_output(self):
        self._initialize()

    @DontOverride
    def _get_value(self) -> bytes:
        """ Overriding to change the type annotation """


class StopReasonParser(SingleValueStatefulParser, initial_value=Reason.EMPTY):
    def _read_and_process_new_data(self):
        lines = self._clear_lines()
        for indicator, reason in self.emulator.REASON_MAPPING.items():
            if indicator in lines:
                self.value = reason

    @DontOverride
    def _get_value(self) -> Reason:
        """ Overriding to change the type annotation """


class DebuggerOutputParser(StatefulParser):
    """
    A parser that determines if the debugger is ready to accept new commands or not.
    """

    emulator: 'DebuggedEmulator'

    def __init__(self, input: BytesIO, emulator: 'Emulator', delimiter: bytes):
        super().__init__(input, emulator)
        self.delimiter = delimiter
        self._outputs_to_skip = 0
        self._outputs = []

    def _add_output(self, output: bytes):
        if self._outputs_to_skip > 0:
            self._outputs_to_skip -= 1
        else:
            self._outputs.append(output)

    def skip_next_output(self):
        if len(self._outputs) > 0:
            self._outputs.pop(0)
        else:
            self._outputs_to_skip += 1

    def _read_and_process_new_data(self):
        data = self._get_buffer()
        output_end = -len(self.delimiter)
        while True:
            output_start = output_end + len(self.delimiter)
            output_end = data.find(self.delimiter, output_start)
            if output_end == -1:
                break
            self._add_output(data[output_start:output_end])
        self._clear(data[output_start:])

    def get_next_output(self) -> bytes:
        self._read_and_process_new_data()
        while len(self._outputs) == 0:
            time.sleep(0.05)
            self._read_and_process_new_data()
        return self._outputs.pop(0)

    def are_any_skips_left(self):
        self._read_and_process_new_data()
        return self._outputs_to_skip > 0
