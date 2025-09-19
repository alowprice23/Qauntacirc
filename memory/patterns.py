from __future__ import annotations
from typing import Dict, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from memory.constellation import ConstellationMemory

class PatternAnalyzer:
    """Analyzes the knowledge graph to find interesting patterns."""

    def __init__(self, memory: 'ConstellationMemory'):
        self.memory = memory

    def find_frequent_relations(self, min_support: int = 2) -> Dict:
        """
        Finds frequent relationships between node types.

        For example, {('REQUIREMENT', 'implements', 'FACT'): 5}
        """
        relation_counts = defaultdict(int)
        for u, v, data in self.memory.graph.edges(data=True):
            relation_type = data.get("relation")
            if not relation_type or relation_type == "similar_to":
                continue

            u_node = self.memory.node_index.get(u)
            v_node = self.memory.node_index.get(v)

            if u_node and v_node:
                pattern = (u_node.type.name, relation_type, v_node.type.name)
                relation_counts[pattern] += 1

        frequent_patterns = {
            "patterns": {str(k): v for k, v in relation_counts.items() if v >= min_support},
            "description": f"Found relationship patterns with minimum support {min_support}"
        }
        return frequent_patterns

    def find_contradiction_clusters(self) -> Dict:
        """Finds clusters of contradictory facts."""
        contradiction_edges = [
            (u, v) for u, v, data in self.memory.graph.edges(data=True)
            if data.get("relation") == "contradicts"
        ]

        # Build a subgraph of contradictions to find connected components (clusters)
        contradiction_graph = self.memory.graph.edge_subgraph(contradiction_edges)
        clusters = [
            list(cluster) for cluster in nx.connected_components(contradiction_graph.to_undirected())
        ]

        return {
            "clusters": clusters,
            "count": len(clusters),
            "description": "Found clusters of contradictory nodes."
        }
