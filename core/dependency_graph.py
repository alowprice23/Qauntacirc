# core/dependency_graph.py

"""
Constructs and analyzes a dependency graph from software modules.
"""

from __future__ import annotations
from typing import List, Tuple
import networkx as nx

from math_utils.laplacian_analyzer import LaplacianAnalyzer

class DependencyGraph:
    """
    Represents the dependency graph of a software system.
    """

    def __init__(self, modules: List[str], dependencies: List[Tuple[str, str]]):
        """
        Initializes the dependency graph.

        Args:
            modules: A list of module names.
            dependencies: A list of tuples representing dependencies (source, target).
        """
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(modules)
        self.graph.add_edges_from(dependencies)

    def calculate_coupling(self) -> float:
        """
        Calculates the coupling energy of the graph.
        """
        # The Laplacian is typically defined for undirected graphs.
        # We'll use the underlying undirected graph for coupling calculation.
        undirected_graph = self.graph.to_undirected()
        analyzer = LaplacianAnalyzer(undirected_graph)
        return analyzer.coupling_energy()
