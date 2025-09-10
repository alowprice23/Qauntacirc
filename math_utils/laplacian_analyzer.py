# math_utils/laplacian_analyzer.py

"""
Provides a class for graph Laplacian analysis.
"""

from __future__ import annotations
import numpy as np
import networkx as nx
from .laplacian import get_combinatorial_laplacian

class LaplacianAnalyzer:
    """
    Analyzes graph properties using the Laplacian matrix.
    """

    def __init__(self, graph: nx.Graph):
        """
        Initializes the analyzer with a NetworkX graph.
        """
        if not isinstance(graph, nx.Graph):
            raise TypeError("Input must be a NetworkX Graph object.")

        if isinstance(graph, nx.DiGraph):
            self.graph = graph.to_undirected()
        else:
            self.graph = graph

        self.adj_matrix = nx.to_numpy_array(self.graph)

    def laplacian_matrix(self) -> np.ndarray:
        """
        Computes the Laplacian matrix of the graph.
        L = D - A
        """
        return get_combinatorial_laplacian(self.adj_matrix)

    def eigenvalues(self) -> np.ndarray:
        """
        Computes the eigenvalues of the Laplacian matrix.
        """
        L = self.laplacian_matrix()
        return np.linalg.eigvalsh(L)

    def coupling_energy(self) -> float:
        """
        Calculates the coupling energy, defined as the trace of the Laplacian.
        E_coupling = Tr(L) = Σᵢ λᵢ
        """
        # The trace of the Laplacian is also twice the number of edges.
        return float(2 * self.graph.number_of_edges())
