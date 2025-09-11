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

    def compute_distance(self, state_a: QCState, state_b: QCState, metric: str = 'fidelity') -> float:
        if not self.is_valid_state(state_a) or not self.is_valid_state(state_b):
            raise ValueError("One or both states are not valid in this state space.")

        vec_a = np.array(state_a.quantum_state.state_vector)
        vec_b = np.array(state_b.quantum_state.state_vector)

        if metric == 'fidelity':
            fidelity = np.abs(np.dot(vec_a.conj(), vec_b))**2
            return np.sqrt(1 - fidelity)
        elif metric == 'euclidean':
            return np.linalg.norm(vec_a - vec_b)
        else:
            raise ValueError(f"Unsupported distance metric: {metric}")

class StateSpaceMetric:
    def __init__(self, metric: str = 'fidelity'):
        self.metric = metric

    def distance(self, state_space: StateSpace, state_a: QCState, state_b: QCState) -> float:
        return state_space.compute_distance(state_a, state_b, self.metric)
