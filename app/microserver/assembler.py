from contextlib import contextmanager
from subprocess import Popen, PIPE
from tempfile import gettempdir
from pathlib import Path
from typing import List
from uuid import uuid4

TMP_DIR = Path(gettempdir(), 'MicroASM')
ASSEMBLER = 'naken_asm'
DISASSEMBLER = 'naken_util'
ASM_TEMPLATE = '.msp430\n.export start\nstart:{asm}\n'

TMP_DIR.mkdir(exist_ok=True)


@contextmanager
def tmpfile() -> Path:
    path = TMP_DIR / str(uuid4())
    try:
        yield path
    finally:
        if path.is_file():
            path.unlink()


class AssemblerException(Exception):
    def __init__(self, output: str):
        self.output = output


def strip_error(assembler_out: bytes, in_file: bytes) -> bytes:
    start = b'Error: '
    end = b'** Errors... bailing out'
    if start in assembler_out and end in assembler_out:
        assembler_out = assembler_out[assembler_out.find(start) + len(start):assembler_out.find(end)]
    return assembler_out.replace(in_file, b'<IN>')


def run_assembler(cmd: List[str], in_file: str) -> bytes:
    process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    code = process.wait()
    output = process.stdout.read()
    if code != 0:
        output += process.stderr.read()
        raise AssemblerException(strip_error(output, in_file.encode()).decode())
    return output


def assemble(asm: str) -> bytes:
    # TODO: use /dev/stdin or a fifo to speed things up
    with tmpfile() as in_file:
        with tmpfile() as out_file:
            in_file.write_text(ASM_TEMPLATE.format(asm=asm))
            run_assembler([ASSEMBLER, '-b', '-o', str(out_file), str(in_file)], str(in_file))
            return out_file.read_bytes()


def disassemble(opcodes: bytes) -> str:
    with tmpfile() as in_file:
        in_file.write_bytes(opcodes)
        output = run_assembler([DISASSEMBLER, '-disasm', '-msp430', '-bin', str(in_file)], str(in_file))
        return output[output.find(b'Addr   '):].decode()
