import logging
import multiprocessing
from typing import Iterator, NamedTuple, Optional

from more_itertools import partition

from .error import IDLParseError
from .webidl import parse, validate
from .webidl.nodes import Ast


logger = logging.getLogger(__name__)


class ParseResult(NamedTuple):

    item: Optional[Ast] = None
    error: Optional[str] = None


def parse_idl(file: str) -> ParseResult:
    try:
        return ParseResult(item=parse(file))
    except IDLParseError:
        return ParseResult(error='Skipped {file}\n{errors}'.format(
            file=file, errors='\n'.join(map(str, validate(file)))))
    except Exception as exc:
        return ParseResult(error=str(exc))


def process_idl(idl_files: tuple[str, ...]) -> list[Ast]:
    return IDLProcessor(idl_files).process()


class IDLProcessor:

    def __init__(self, idl_files: tuple[str, ...], process: int = 4):
        self._idl_files = idl_files
        self._process = process

    def process(self) -> list[Ast]:
        return self.parse()

    def _parse(self) -> Iterator[ParseResult]:
        with multiprocessing.Pool(self._process) as pool:
            yield from pool.imap_unordered(parse_idl, self._idl_files)

    def parse(self) -> list[Ast]:
        successes, fails = partition(
            pred=lambda result: result.item is None, iterable=self._parse())

        for fail in fails:
            logger.debug(fail.error)

        return [success.item for success in successes]  # type: ignore
