from pathlib import Path
from typing import Tuple

from storage import Storage
from converter import InterfaceTransformer
from webidl.nodes import Ast as WebIDLAst
from unparser import unparse
from idl_processor import IDLProcessor
from builder import Builder, try_statement
from built_in_types import BuiltInTypes


class Idl2Js:

    def __init__(self, idl: Tuple[str, ...], output: str):
        self._storage = Storage()
        self._std_types = BuiltInTypes()
        self._builder = Builder(storage=self._storage, std_types=self._std_types)
        self._idl_processor = IDLProcessor(idl)

        self._output = output

        self._make_variables()
        self._save('1.js')

    def _make_variables(self):
        InterfaceTransformer[WebIDLAst](
            storage=self._storage,
            builder=self._builder,
        ).visit(self._idl_processor.run()[0])

    def _save(self, file_name):
        with open(Path(self._output) / file_name, 'w') as f:
            f.write('\n'.join(self.generate()))

    def generate(self):
        return [
            unparse(try_statement(variable.ast))
            for variable in self._storage._var
        ]


def main():
    raw_idl = (Path(__file__).parent.parent / 'blob.webidl').resolve()
    idl2js = Idl2Js(idl=(str(raw_idl),), output=str(Path('.output').resolve()))
    print(idl2js.generate())


if __name__ == '__main__':
    main()
