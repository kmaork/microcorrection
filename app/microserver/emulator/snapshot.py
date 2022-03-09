from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple


class Reason(Enum):
    LOSE_REASON = 'CPUOFF flag set; program no longer running. CPU must now be reset.'
    UNALIGNED_REASON = 'insn address unaligned'
    DEBUG_WIN_REASON = 'Door Unlocked.'
    REAL_WIN_REASON = ''
    EMPTY = ''


class State(Enum):
    BREAKPOINT = '0'
    WORKING = '1'
    STOPPED = '2'
    PROMPT = '4'


class Advance(Enum):
    NOPE = False
    DEBUG_WIN = True
    WIN = 'win'


@dataclass
class EmulatorSnapshot:
    state: State
    new_output: bytes
    update_memory: Dict[int, bytes]  # maps between address and 16 bytes of non null memory
    advanced: Advance
    instructions: int
    regs: Tuple[int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int]
    pc: int
    stop_reason: Reason
    disasm: bytes
    insn_bytes: bytes
