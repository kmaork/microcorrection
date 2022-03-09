import re
import time
from functools import wraps
from pathlib import Path
from subprocess import Popen
from typing import Any, Callable, List
from flask import current_app, has_app_context

from .emulator import Emulator
from .debugger_commands import DbgCommand, SingleResultDbgCommand, MultipleResultDbgCommand
from .utils import ExtendSuperList, ReaderThread, unhex, Mutable, UpdateSuperDict, remove_extra_whitespace
from .snapshot import State, Reason
from .stateful_parser import DebuggerOutputParser
from .exceptions import EmulatorStoppedException
from ..utils import thread_safe

'''
WTF sometimes 100% CPU?

Can we make continue non blocking in the emulator???????????

Maybe make continue blocking so we can check if it stopped due to breakpoint.

Known bugs:
there is a state in which two commands are executed, and dbg data is not checked between them.
then, the second command might be executed when on the custom breakpoint.
reg bp: return reg and stay
step bp: step only after continued
cont bp

TODO: connect to the socket directly and use the gdb rsp client to debug instead of using the tui and parsing results.
https://github.com/stef/pyrsp
'''


# TODO: enter to send solution, quick way to make hex encoded
# TODO: why after input we get a lot of snapshot requests?

# TODO: add buttons to download ida plugin and maybe gdb stuff

# TODO: this is a symptom
def return_last_result_if_cant_debug(initial_value):
    def decorator(func: Callable):
        last_val = Mutable(initial_value)

        @wraps(func)
        def wrapper(self: 'DebuggedEmulator', *args, **kwargs):
            if not self._can_debug():
                return last_val.val
            new_val = func(self, *args, **kwargs)
            last_val.val = new_val
            return new_val

        return wrapper

    return decorator


def default_if_cant_debug(value):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self: 'DebuggedEmulator', *args, **kwargs):
            if not self._can_debug():
                return value
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class DebuggedEmulator(Emulator):
    IS_DEBUGGED = True
    REMOVE_OUTPUT_REGEXES = ExtendSuperList([
        br'GDB stub listening on \[\*\]:3713\n',
        br'Waiting for client to connect\.\.\.\n',
        br'GDB client connected\.\n',
        br'XXX Got unhandled .+\n',
    ])
    REASON_MAPPING = UpdateSuperDict({
        # The hardcoded superclass reference is ugly but will be solved when this will be an argument to the parser
        Emulator.WIN_STR: Reason.DEBUG_WIN_REASON
    })

    DEBUGGER = 'msp430-gdb'
    DBG_PROMPT = b'(gdb) '

    INTERRUPT_ADDR = 0x10
    PROMPT_SR_VALUE = 0x8200
    MAX_SP = 0x4400
    MEMORY_SIZE = 0x10000
    MEM_CHUNK_SIZE = 16
    MEM_CHUNK_ADDRS = range(0, MEMORY_SIZE, MEM_CHUNK_SIZE)

    IS_BEFORE_PROMPT_EXPR = f'$r2=={PROMPT_SR_VALUE}&&$pc=={INTERRUPT_ADDR}'.encode()
    IS_INSN_RET_EXPR = b'*(int)$pc==16688'

    PRINT_PC = SingleResultDbgCommand(b'p/d $pc', br' = (\d+)', int)
    PRINT_SP = SingleResultDbgCommand(b'p/d $sp', br' = (\d+)', int)
    SHOW_REGS = MultipleResultDbgCommand(b'i r', br': ([0-9a-fA-F]{4})', unhex)
    # TODO: If we're already patching the emulator, why not add a specific API for us to record memory changes or to dump only non-null memory?
    SHOW_MEM = DbgCommand(b'dump binary memory /dev/stdout 0 0x10000')
    SHOW_INSN = SingleResultDbgCommand(b'x/i $pc', br'0x.+:\s*(.+)', remove_extra_whitespace)
    NEXT_INSN_ADDR = SingleResultDbgCommand(b'x/2i $pc', br'\n\s*0x(.+):', unhex)

    CONT_UNTIL_BREAKPOINT = SingleResultDbgCommand(b'c', br'(?:Break|Watch)point (\d+)[:,]')
    CONT = DbgCommand(b'c')
    STEP = DbgCommand(b'si')

    def __init__(self, emu_process: Popen, dbg_process: Popen, dbg_port: int):
        super().__init__(emu_process)
        self.dbg_process = dbg_process
        self.dbg_port = dbg_port
        self.dbg_reader = ReaderThread(dbg_process.stdout)
        self._debugger_state_parser = DebuggerOutputParser(self.dbg_reader.get_output_stream(), self, self.DBG_PROMPT)
        self.dbg_reader.start()
        self._last_memory = {i: b'\0' * self.MEM_CHUNK_SIZE for i in self.MEM_CHUNK_ADDRS}
        self._memory_updates = {}
        self._breakpoints = {}

    @thread_safe
    def _initialize_debugger(self):
        """
        Configure the debugger.
        We are setting a watchpoint to stop right before a prompt interrupt, to we can retrieve debugging data.
        Microcorruption doesn't allow the user to set a breakpoint on the interrupt trap address,
        so our watchpoint won't be confused with user breakpoints.
        """
        self._debugger_state_parser.skip_next_output()  # Skip all output until the first (gdb) prompt
        self._run_dbg_command(DbgCommand(b'set confirm off'))
        self._run_dbg_command(DbgCommand(f'target remote localhost:{self.dbg_port}'.encode()))
        self._run_dbg_command(DbgCommand(b'watch ' + self.IS_BEFORE_PROMPT_EXPR))

    def _get_state(self) -> State:
        if self.dbg_process.poll() is not None:
            return State.STOPPED
        emulator_state = super(DebuggedEmulator, self)._get_state()
        if self._prompt_available() and emulator_state is not State.STOPPED:
            return State.BREAKPOINT
        return emulator_state

    def _prompt_available(self):
        return not self._debugger_state_parser.are_any_skips_left()  # No skips left means all commands ran

    def _can_debug(self):
        return self._get_state() is State.BREAKPOINT

    @thread_safe
    def get_update_memory(self):
        if self._can_debug():
            mem_dump = self._get_dbg_cmd_result(self.SHOW_MEM)
            assert len(mem_dump) == self.MEMORY_SIZE
            cur_mem_dict = {i: mem_dump[i:i + self.MEM_CHUNK_SIZE] for i in self.MEM_CHUNK_ADDRS}
            update = {i: cur_mem_dict[i] for i in self.MEM_CHUNK_ADDRS if cur_mem_dict[i] != self._last_memory[i]}
            self._memory_updates.update(update)
        return dict(self._memory_updates)

    @thread_safe
    def sent_memory_updates(self):
        # TODO: here and in the UserOutputParser, I implemented this type of function to make sure that
        # all memory updates get to the user and don't get lost when just called. But this is a race! :(
        # we don't know the updates that were sent were necessarily the last updates.
        self._last_memory.update(self._memory_updates)
        self._memory_updates.clear()

    @return_last_result_if_cant_debug(Emulator.UNKNOWN_REGS)
    @thread_safe
    def get_regs(self) -> List[int]:
        return self._get_dbg_cmd_result(self.SHOW_REGS)

    @return_last_result_if_cant_debug(Emulator.UNKNOWN_PC)
    @thread_safe
    def _get_pc(self):
        return self._get_dbg_cmd_result(self.PRINT_PC)

    @return_last_result_if_cant_debug(Emulator.UNKNOWN_INSN)
    @thread_safe
    def _get_insn(self) -> bytes:
        return self._get_dbg_cmd_result(self.SHOW_INSN)

    @thread_safe
    def _get_next_insn_addr(self) -> int:
        return self._get_dbg_cmd_result(self.NEXT_INSN_ADDR)

    @return_last_result_if_cant_debug(Emulator.UNKNOWN_INSN_BYTES)
    @thread_safe
    def _get_insn_bytes(self) -> bytes:
        pc = self._get_pc()
        return self.get_mem(pc, self._get_next_insn_addr() - pc)

    def _check_bool(self, bool_expr: bytes) -> bool:
        cmd = SingleResultDbgCommand(b'p ' + bool_expr, br'\$\d+ = ([01])', lambda n: bool(int(n)))
        return self._get_dbg_cmd_result(cmd)

    def _is_in_pre_prompt_breakpoint(self) -> bool:
        if not self.is_alive():
            return False
        return self._prompt_available() and self._check_bool(self.IS_BEFORE_PROMPT_EXPR)

    @thread_safe
    def _handle_pre_prompt(self):
        super()._get_dbg_data()
        self.step(False)
        while not self._get_state() is State.PROMPT:
            time.sleep(0.05)

    @thread_safe
    def cont(self):
        # TODO: should we give live updates? At least when the cpu dies, micro returns new register values.
        self._run_dbg_command(self.CONT, False)

    @thread_safe
    def blocont(self) -> bytes:
        return self._get_dbg_cmd_result(self.CONT_UNTIL_BREAKPOINT)

    @thread_safe
    def step(self, wait=True):
        # TODO: important: this step might be stuck forever if there is a prompt!
        self._run_dbg_command(self.STEP, wait_for_result=wait)

    @thread_safe
    def step_n(self, step_n: int):
        self._run_dbg_command(DbgCommand(b'si ' + str(step_n).encode()))

    @thread_safe
    def step_over(self):
        next_insn_addr = self._get_next_insn_addr()
        breakpoint_cmd = SingleResultDbgCommand(b'break *' + str(next_insn_addr).encode(), br'Breakpoint (\d+) at')
        breakpoint_id = self._get_dbg_cmd_result(breakpoint_cmd)
        self.blocont()
        self._run_dbg_command(DbgCommand(b'delete ' + breakpoint_id))
        if self._is_in_pre_prompt_breakpoint():
            self._handle_pre_prompt()

    @thread_safe
    def step_out(self):
        sp = self._get_dbg_cmd_result(self.PRINT_SP)
        sp_bytes = str(self.MAX_SP if sp == 0 else sp).encode()
        if self._check_bool(self.IS_INSN_RET_EXPR):
            self.step(False)
            return
        break_on_ret = SingleResultDbgCommand(b'watch ' + self.IS_INSN_RET_EXPR + b'&&$sp>=' + sp_bytes,
                                              br'Watchpoint (\d+):')
        watchpoint_id = self._get_dbg_cmd_result(break_on_ret)
        current_watchpoint_id = self.blocont()
        self._run_dbg_command(DbgCommand(b'delete ' + watchpoint_id))

        if self._is_in_pre_prompt_breakpoint():
            self._handle_pre_prompt()
        elif watchpoint_id == current_watchpoint_id:
            self.step(False)

    @thread_safe
    def set_breakpoint(self, addr: int):
        cmd = SingleResultDbgCommand(b'break *' + str(addr).encode(), br'Breakpoint (\d+) at')
        self._breakpoints[addr] = self._get_dbg_cmd_result(cmd)

    @thread_safe
    def delete_breakpoint(self, addr: int):
        # TODO: throw a 400 if doesn't exist?
        breakpoint_id = self._breakpoints[addr]
        cmd = DbgCommand(b'delete ' + breakpoint_id)
        assert self._get_dbg_cmd_result(cmd) == b''
        del self._breakpoints[addr]

    def get_breakpoint_addrs(self):
        return self._breakpoints.keys()

    @thread_safe
    def set_reg(self, reg_i: int, reg_val: int) -> None:
        self._run_dbg_command(DbgCommand(f'set $r{reg_i}={reg_val}'.encode()))

    @thread_safe
    def set_mem(self, addr: int, val: int) -> None:
        self._run_dbg_command(DbgCommand(f'set *{addr}={val}'.encode()))

    @thread_safe
    def get_mem(self, addr: int, len: int) -> bytes:
        return self._get_dbg_cmd_result(DbgCommand(f'dump binary memory /dev/stdout {addr} {addr + len}'.encode()))

    def _assert_alive(self):
        if not self.is_alive():
            raise EmulatorStoppedException('Emulator stopped unexpectedly')

    @thread_safe
    def _run_dbg_command(self, command: DbgCommand, wait_for_result=True):
        if self.is_alive():
            self.dbg_process.stdin.write(command.cmd + b'\n')
            result = None
            if wait_for_result:
                result = self._debugger_state_parser.get_next_output()
            else:
                self._debugger_state_parser.skip_next_output()
            self._assert_alive()
            return result

    @thread_safe
    def _get_dbg_cmd_result(self, command: DbgCommand) -> Any:
        output = self._run_dbg_command(command)
        return command.parse(output)

    @thread_safe
    def _get_dbg_data(self):
        """
        If we are before a prompt interrupt, first get dbg data and then continue for the prompt to happen.
        """
        if self._is_in_pre_prompt_breakpoint():
            self._handle_pre_prompt()
        return super()._get_dbg_data()

    @thread_safe
    def kill(self) -> None:
        super().kill()
        if has_app_context():
            current_app.logger.debug('Killing debugger')
        self.dbg_process.kill()

    @classmethod
    def _get_fresh_emu_process_dbg_port(cls, emu_process: Popen) -> int:
        # TODO: should we use a stateful parser for this?
        emu_process.stdout.readline()
        line = emu_process.stdout.readline()
        return int(re.search(rb'GDB stub listening on \[\*\]:(\d+)', line).group(1))

    @classmethod
    def run(cls, rom: Path):
        current_app.logger.debug('Running debugged emulator')
        emu_process = Popen([cls.EXECUTABLE, '-g', str(rom)], **cls._get_popen_kwargs())
        current_app.logger.debug('Running debugger')
        dbg_process = Popen([cls.DEBUGGER], **cls._get_popen_kwargs())
        instance = cls(emu_process, dbg_process, cls._get_fresh_emu_process_dbg_port(emu_process))
        instance._initialize_debugger()
        return instance
