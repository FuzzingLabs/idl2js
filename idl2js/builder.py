from functools import cached_property
from operator import attrgetter
from collections import deque
from itertools import repeat

from more_itertools import flatten, first_true, first

from .built_in_types import BuiltInTypes
from .converter import convert
from .js.statements import create_literal, create_identifier, create_array


class DefinitionStorage:

    def __init__(self, idls):
        self._definitions = list(flatten(map(attrgetter('definitions'), idls)))

    @cached_property
    def build_definition(self):
        return [
            definition
            for definition in self._definitions
            if definition.type == 'interface' and definition.partial is False
        ]

    def find_by_type(self, idl_type):
        return first_true(self._definitions, pred=lambda definition: definition.name == idl_type)


def get_node_type(node, level=1):
    return attrgetter('.'.join(repeat('idl_type', level)))(node)


class Builder:

    def __init__(self, std_types: BuiltInTypes, definition_storage: DefinitionStorage):
        self._std_types = std_types
        self._definition_storage = definition_storage

    def single(self, idl_type):
        if idl_type in self._std_types:
            return [], create_literal(self._std_types.generate(idl_type))

        converter = convert(
            builder=self,
            definition=self._definition_storage.find_by_type(idl_type)
        )

        return [converter], create_identifier(first(converter.variables).ast.expression.left.name)

    def create(self, node):
        idl_type = get_node_type(node, level=2)

        if isinstance(idl_type, list):
            deps = []
            identifiers = []
            for idl in idl_type:
                dep, identifier = self.single(idl.idl_type)

                deps.extend(dep)
                identifiers.append(identifier)

            return deps, create_array(elements=identifiers)

        return self.single(idl_type)


def build(definition_storage, builder):
    for definition in definition_storage.build_definition:
        result = []

        todo = deque([convert(builder=builder, definition=definition)])
        while todo:
            item = todo.popleft()
            result.append(item.variables)
            todo.extendleft(item.dependencies)

        yield from flatten(reversed(result))
