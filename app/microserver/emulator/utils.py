import re
from io import BytesIO
from threading import Thread
from typing import List, Optional, Any
from functools import partial

unhex = partial(int, base=16)


def remove_extra_whitespace(s: bytes) -> bytes:
    return re.sub(rb'\s+', b' ', s)


class ReaderThread(Thread):
    # TODO: this is shitty. There is no need to support windows anymore and the operations on IO might not be thread safe.
    """
    Using a thread to read a stream because windows doesn't support aio with files
    """

    def __init__(self, input_stream: BytesIO, output_streams: Optional[List[BytesIO]] = None):
        super().__init__()
        self.input_stream = input_stream
        self.output_streams = output_streams or []

    def run(self):
        while True:
            byte = self.input_stream.read(1)
            if not byte:
                break
            for output in self.output_streams:
                output.write(byte)

    def get_output_stream(self) -> BytesIO:
        assert not self.is_alive(), 'Can\'t add outputs after started running'
        output = BytesIO()
        self.output_streams.append(output)
        return output

    def cleanup(self):
        # TODO: should this be called sometime?
        for output in self.output_streams:
            output.close()


class ExtendSuperList:
    def __init__(self, lst: list):
        self.lst = lst

    def __set_name__(self, owner, name):
        super_lst = getattr(super(owner, owner), name, [])
        self.lst = super_lst + self.lst

    def __get__(self, instance, owner):
        return self.lst


class UpdateSuperDict:
    def __init__(self, dct: dict):
        self.dct = dct

    def __set_name__(self, owner, name):
        super_dct = getattr(super(owner, owner), name, {})
        self.dct = {**super_dct, **self.dct}

    def __get__(self, instance, owner):
        return self.dct


class DontOverride:
    def __init__(self, func):
        """ We don't need the func """

    def __set_name__(self, owner, name):
        delattr(owner, name)


class Mutable:
    __slots__ = ['val']

    def __init__(self, val: Any):
        self.val = val
