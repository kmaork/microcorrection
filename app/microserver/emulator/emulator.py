import re
from pathlib import Path
from subprocess import Popen, PIPE
from flask import current_app, has_app_context

from .utils import ReaderThread
from .stateful_parser import CPUStateParser, LevelAdvanceParser, InstructionAmountParser, UserOutputParser, \
    StopReasonParser
from .snapshot import State, Advance, EmulatorSnapshot, Reason
from ..session_storage import Storable
from ..utils import ThreadSafe, thread_safe


class Emulator(Storable, ThreadSafe):
    IS_DEBUGGED = False
    EXECUTABLE = 'msp430-emu'

    WIN_STR = b'The lock opens; you win!'
    CPU_OFF_STR = b'Got CPUOFF, stopped.'
    INSTRUCTIONS_REGEX = br'instructions per second \(Total: (\d+)\)\.'
    PROMPT_STR = b'Gets (\':\'-prefix for hex)> '
    REMOVE_OUTPUT_REGEXES = [
        br'Loaded \d+ words from image\.\n',
        br'Initial register state:\n',
        br'pc  (.*\n)* {6}( {2}[0-9a-fA-F]{4}){4}\n',  # register dump
        br'={44}\n\n',  # line of '='
        br'Approx\. \d+ instructions per second \(Total: \d+\)\.\n',
        re.escape(CPU_OFF_STR + b'\n'),
        re.escape(PROMPT_STR),
        re.escape(WIN_STR + b'\n')
    ]
    REASON_MAPPING = {
        CPU_OFF_STR: Reason.LOSE_REASON,
        WIN_STR: Reason.REAL_WIN_REASON,
        b'insn addr unaligned': Reason.UNALIGNED_REASON
    }

    UNKNOWN_MEMORY = {}
    UNKNOWN_REGS = (0,) * 16
    UNKNOWN_PC = 0
    UNKNOWN_INSN = b''
    UNKNOWN_INSN_BYTES = b''

    def __init__(self, emu_process: Popen):
        super().__init__()
        self.emu_process = emu_process
        self.emu_reader = ReaderThread(self.emu_process.stdout)
        self._state_parser = CPUStateParser(self.emu_reader.get_output_stream(), self)
        self._advance_parser = LevelAdvanceParser(self.emu_reader.get_output_stream(), self)
        self._instruction_amount_parser = InstructionAmountParser(self.emu_reader.get_output_stream(), self)
        self._user_output_parser = UserOutputParser(self.emu_reader.get_output_stream(), self)
        self._stop_reason_parser = StopReasonParser(self.emu_reader.get_output_stream(), self)
        self.emu_reader.start()

    def is_alive(self) -> bool:
        return self._get_state() is not State.STOPPED

    @thread_safe
    def kill(self) -> None:
        if has_app_context():
            current_app.logger.debug('Killing emulator')
        self.emu_process.kill()

    @thread_safe
    def write_input_to_emulator(self, input_bytes: bytes):
        self.emu_process.stdin.write(f':{input_bytes.hex()}\n'.encode())
        self._state_parser.input_was_provided()

    @thread_safe
    def cont(self):
        # TODO: in the original server, the process doesn't run until continue and input isn't applied until continue
        pass

    def _get_state(self) -> State:
        if self.emu_process.poll() is not None:
            return State.STOPPED
        return self._state_parser.get_value()

    def _get_advance(self) -> Advance:
        return self._advance_parser.get_value()

    def _get_instructions(self) -> int:
        return self._instruction_amount_parser.get_value()

    def _get_reason(self) -> Reason:
        return self._stop_reason_parser.get_value()

    def _get_insn(self) -> bytes:
        return self.UNKNOWN_INSN

    def _get_insn_bytes(self) -> bytes:
        return self.UNKNOWN_INSN_BYTES

    def _strip_output(self) -> bytes:
        return self._user_output_parser.get_value()

    def get_update_memory(self):
        return self.UNKNOWN_MEMORY

    @thread_safe
    def sent_memory_updates(self):
        pass

    def get_regs(self):
        return self.UNKNOWN_REGS

    def _get_pc(self):
        return self.UNKNOWN_PC

    def _get_dbg_data(self):
        """
        We separate _get_dbg_data from other snapshot data to be overridden by subclasses
        """
        return self.get_update_memory(), self.get_regs(), self._get_pc()

    @thread_safe
    def get_snapshot(self) -> EmulatorSnapshot:
        update_memory, regs, pc = self._get_dbg_data()
        snap = EmulatorSnapshot(
            state=self._get_state(),
            new_output=self._strip_output(),
            advanced=self._get_advance(),
            instructions=self._get_instructions(),
            update_memory=update_memory,
            regs=regs,
            pc=pc,
            stop_reason=self._get_reason(),
            disasm=self._get_insn(),
            insn_bytes=self._get_insn_bytes()
        )
        self._user_output_parser.sent_new_output()
        self.sent_memory_updates()
        return snap

    @classmethod
    def _get_popen_kwargs(cls):
        return dict(close_fds=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=0)

    @classmethod
    def run(cls, rom: Path):
        current_app.logger.debug('Running emulator')
        return cls(Popen([cls.EXECUTABLE, str(rom)], **cls._get_popen_kwargs()))

    @thread_safe
    def __del__(self):
        self.kill()
