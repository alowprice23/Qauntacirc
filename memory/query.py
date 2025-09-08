class MemoryQuery:
    def __init__(self, search_term, memory_type, limit):
        self.search_term = search_term
        self.memory_type = memory_type
        self.limit = limit

class QueryBuilder:
    def __init__(self):
        self._search_term = ""
        self._memory_type = "all"
        self._limit = 10

    def search(self, search_term):
        self._search_term = search_term
        return self

    def type(self, memory_type):
        self._memory_type = memory_type
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def build(self):
        return MemoryQuery(self._search_term, self._memory_type, self._limit)
