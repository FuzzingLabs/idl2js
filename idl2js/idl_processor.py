import logging
from pathlib import Path
from typing import List, Optional, Tuple

from error import IDLParseError
from webidl import parse, validate
from webidl.nodes import Ast


logger = logging.getLogger(__name__)


def parse_idl(file: str) -> Optional[Ast]:
    try:
        return parse(file)
    except IDLParseError:
        errors = '\n'.join(map(str, validate(file)))
        logger.debug(f'Skipped {file}\n{errors}')


class IDLProcessor:
    def __init__(self, idl_files: Tuple[str, ...]):
        self._idl_files = idl_files

    def run(self) -> List[Ast]:
        return list(filter(None, map(parse_idl, self._idl_files)))


def main():
    raw_idl = (Path(__file__).parent / 'idl' / 'std' / 'blob.webidl').resolve()
    processor = IDLProcessor((str(raw_idl),))
    print(processor.run())


if __name__ == '__main__':
    main()
