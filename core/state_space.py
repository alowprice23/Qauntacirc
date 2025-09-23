"""
State Space
"""
from typing import List
import numpy as np
from core.types import QCState

class StateSpace:
    def __init__(self, dimension: int):
        if dimension <= 0:
            raise ValueError("State space dimension must be positive.")
        self.dimension = dimension

    def get_dimension(self) -> int:
        return self.dimension

    def is_valid_state(self, state: QCState) -> bool:
        if not state.quantum_state:
            return False
        if len(state.quantum_state.state_vector) != self.dimension:
            return False
        if not np.isclose(np.linalg.norm(state.quantum_state.state_vector), 1.0):
            return False
        return True

    def get_basis_vector(self, index: int) -> List[float]:
        if not (0 <= index < self.dimension):
            raise IndexError("Basis vector index is out of bounds.")
        vec = np.zeros(self.dimension)
        vec[index] = 1.0
        return vec.tolist()

    def get_random_state_vector(self) -> List[float]:
        vec = np.random.rand(self.dimension) + 1j * np.random.rand(self.dimension)
        vec /= np.linalg.norm(vec)
        return vec.tolist()

    def _ast_edit_distance(self, state_a: QCState, state_b: QCState) -> float:
        # This is a simplified version. A real implementation would compare
        # the ASTs of all modules.
        from math_utils.distance_metrics import levenshtein_distance
        ast_a = state_a.modules[0].normalized_ast if state_a.modules else b""
        ast_b = state_b.modules[0].normalized_ast if state_b.modules else b""
        return levenshtein_distance(ast_a.decode('utf-8'), ast_b.decode('utf-8'))

    def _graph_edit_distance(self, state_a: QCState, state_b: QCState) -> float:
        import networkx as nx
        g_a = nx.DiGraph()
        if state_a.dependency_graph:
            g_a.add_nodes_from([n.id for n in state_a.dependency_graph.nodes])
            g_a.add_edges_from([(e.source.id, e.target.id) for e in state_a.dependency_graph.edges])

        g_b = nx.DiGraph()
        if state_b.dependency_graph:
            g_b.add_nodes_from([n.id for n in state_b.dependency_graph.nodes])
            g_b.add_edges_from([(e.source.id, e.target.id) for e in state_b.dependency_graph.edges])

        return nx.graph_edit_distance(g_a, g_b)

    def _test_vector_hamming_distance(self, state_a: QCState, state_b: QCState) -> int:
        tests_a = set(state_a.failing_tests)
        tests_b = set(state_b.failing_tests)
        return len(tests_a.symmetric_difference(tests_b))

    def compute_distance(self, state_a: QCState, state_b: QCState, metric: str = 'composite', weights: dict = None) -> float:
        if weights is None:
            weights = {'ast': 0.5, 'graph': 0.3, 'test': 0.2}

        if metric == 'composite':
            dist_ast = self._ast_edit_distance(state_a, state_b)
            dist_graph = self._graph_edit_distance(state_a, state_b)
            dist_test = self._test_vector_hamming_distance(state_a, state_b)

            # Normalization is needed here. This is a placeholder.
            # A real implementation would need a more robust normalization scheme.
            norm_dist_ast = dist_ast / (max(len(state_a.modules[0].normalized_ast), len(state_b.modules[0].normalized_ast)) if state_a.modules and state_b.modules else 1)
            norm_dist_graph = dist_graph # graph_edit_distance is already a kind of normalized value
            norm_dist_test = dist_test / (len(set(state_a.failing_tests).union(set(state_b.failing_tests))) if set(state_a.failing_tests).union(set(state_b.failing_tests)) else 1)

            return (weights['ast'] * norm_dist_ast +
                    weights['graph'] * norm_dist_graph +
                    weights['test'] * norm_dist_test)

        elif metric in ['fidelity', 'euclidean']:
            if not self.is_valid_state(state_a) or not self.is_valid_state(state_b):
                raise ValueError("One or both states are not valid in this state space for fidelity or euclidean distance.")

            vec_a = np.array(state_a.quantum_state.state_vector)
            vec_b = np.array(state_b.quantum_state.state_vector)

            if metric == 'fidelity':
                fidelity = np.abs(np.dot(vec_a.conj(), vec_b))**2
                return np.sqrt(1 - fidelity)
            else: # euclidean
                return np.linalg.norm(vec_a - vec_b)
        else:
            raise ValueError(f"Unsupported distance metric: {metric}")

class StateSpaceMetric:
    def __init__(self, metric: str = 'composite', weights: dict = None):
        self.metric = metric
        self.weights = weights

    def distance(self, state_space: StateSpace, state_a: QCState, state_b: QCState) -> float:
        return state_space.compute_distance(state_a, state_b, self.metric, self.weights)
