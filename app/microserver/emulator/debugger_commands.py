from abc import abstractmethod, ABCMeta
import re
from typing import Any, List

from .exceptions import DbgCommandOutputParsingException


class DbgCommand:
    def __init__(self, cmd: bytes):
        self.cmd = cmd

    def parse(self, output: bytes) -> Any:
        return output


class ParsableDbgCommand(DbgCommand, metaclass=ABCMeta):
    def __init__(self, cmd: bytes, pattern: bytes, parser=lambda x: x):
        super().__init__(cmd)
        self.pattern = re.compile(pattern)
        self.parser = parser

    @abstractmethod
    def _get_output(self, output: bytes) -> Any:
        pass

    def _parse_output(self, output: bytes) -> Any:
        return self.parser(output)

    def parse(self, output: bytes) -> Any:
        return self._parse_output(self._get_output(output))


class SingleResultDbgCommand(ParsableDbgCommand):
    def _get_output(self, output: bytes) -> bytes:
        result = re.search(self.pattern, output)
        if result is None:
            raise DbgCommandOutputParsingException(self, output)
        return result.group(1)


class MultipleResultDbgCommand(ParsableDbgCommand):
    def _get_output(self, output: bytes) -> List[bytes]:
        return re.findall(self.pattern, output)

    def _parse_output(self, output: bytes) -> List:
        return list(map(self.parser, output))
