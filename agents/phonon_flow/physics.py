import numpy as np
import math
from typing import List
from core.types import CommunicationGraph, DispersionRelation, OptimizedChannel

class LatticeModel:
    """A model to represent a communication graph as a physical lattice."""
    def __init__(self, graph: CommunicationGraph):
        self.graph = graph
        self.node_map = {node.id: i for i, node in enumerate(graph.nodes)}
        self.adj_matrix = self._create_adj_matrix()

    def _create_adj_matrix(self) -> np.ndarray:
        n = len(self.graph.nodes)
        adj = np.zeros((n, n))
        for edge in self.graph.edges:
            i = self.node_map.get(edge.source.id)
            j = self.node_map.get(edge.target.id)
            if i is not None and j is not None:
                adj[i, j] = edge.weight
                adj[j, i] = edge.weight
        return adj

    def k_space_sampling(self) -> List[np.ndarray]:
        """A simplified sampling of the Brillouin zone."""
        return [np.array([kx, ky]) for kx in [-1, 0, 1] for ky in [-1, 0, 1] if kx != 0 or ky != 0]

    def get_avg_spring_constant(self) -> float:
        """Acoustic modes relate to the average 'stiffness' (dependency strength)."""
        strengths = self.adj_matrix[self.adj_matrix > 0]
        return np.mean(strengths) if strengths.size > 0 else 0.0

    def get_stiffness_variance(self) -> float:
        """Optical modes relate to the variance in 'stiffness'."""
        strengths = self.adj_matrix[self.adj_matrix > 0]
        return np.var(strengths) if strengths.size > 0 else 0.0

class LatticeDynamics:
    def __init__(self, hbar=1.0, min_efficiency_threshold=0.5):
        self.hbar = hbar
        self.min_efficiency_threshold = min_efficiency_threshold

    def map_to_lattice(self, communication_graph: CommunicationGraph) -> LatticeModel:
        return LatticeModel(communication_graph)

    def compute_sound_velocity(self, lattice: LatticeModel, mode_type: str) -> float:
        """Computes effective sound velocity based on lattice properties (v ~ sqrt(K/m))."""
        if mode_type == "acoustic":
            K = lattice.get_avg_spring_constant()
            return math.sqrt(K) if K > 0 else 0.0
        else:
            K_var = lattice.get_stiffness_variance()
            return 1.0 / (1.0 + math.sqrt(K_var)) if K_var > 0 else 1.0

    def compute_group_velocity(self, v_s: float, k_vector: np.ndarray) -> float:
        """For linear dispersion ω=v_s*k, group velocity equals phase velocity."""
        return v_s

    def compute_bandwidth(self, relation: DispersionRelation) -> float:
        return relation.group_velocity * 10

    def compute_latency_improvement(self, optimizations: List[OptimizedChannel]) -> float:
        if not optimizations: return 0.0
        avg_new_velocity = np.mean([opt.group_velocity for opt in optimizations])
        return (avg_new_velocity - 1.0) * 100
