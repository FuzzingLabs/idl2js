from collections import defaultdict


class Storage:

    def __init__(self):
        self.variables = []
        self._by_type = defaultdict(list)

    def add(self, variable):
        self.variables.append(variable)

    def __setitem__(self, key, value):
        self._by_type[key].append(value)

    def __getitem__(self, item):
        return self._by_type[item]
