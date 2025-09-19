from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from memory.constellation import ConstellationMemory, KnowledgeNode, NodeType

class QueryBuilder:
    """A fluent builder for creating and executing queries against ConstellationMemory."""
    def __init__(self, memory: 'ConstellationMemory'):
        self.memory = memory
        self._search_term: str = ""
        self._limit: int = 10
        self._node_type: 'NodeType' = None
        self._metadata_filter: dict = {}

    def search(self, search_term: str) -> 'QueryBuilder':
        """Set the search term for the query."""
        self._search_term = search_term
        return self

    def with_type(self, node_type: 'NodeType') -> 'QueryBuilder':
        """Filter results by node type."""
        self._node_type = node_type
        return self

    def with_metadata(self, metadata_filter: dict) -> 'QueryBuilder':
        """Filter results by matching metadata."""
        self._metadata_filter = metadata_filter
        return self

    def limit(self, limit: int) -> 'QueryBuilder':
        """Set the maximum number of results to return."""
        self._limit = limit
        return self

    def execute(self) -> List['KnowledgeNode']:
        """Execute the query and return the results."""
        # Fetch more results initially to have enough for filtering.
        candidate_nodes = self.memory.query_facts(self._search_term, limit=self._limit * 5 + 10)

        filtered_nodes = []
        for node in candidate_nodes:
            # Filter by node type
            if self._node_type and node.type != self._node_type:
                continue

            # Filter by metadata
            if self._metadata_filter:
                match = all(item in node.metadata.items() for item in self._metadata_filter.items())
                if not match:
                    continue

            filtered_nodes.append(node)

        return filtered_nodes[:self._limit]
