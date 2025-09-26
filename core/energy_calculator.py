"""
Energy Calculator
"""
from typing import Tuple, Dict, List, Any
import numpy as np
from math_utils.info_entropy import shannon_entropy, kolmogorov_approx
from math_utils.laplacian import calculate_laplacian_trace

# Assuming a QCState object structure for type hinting
from .types import QCState

class EnergyCalculator:
    def __init__(self, alpha: float, beta: float, gamma: float, delta: float, **kwargs):
        if not all(w >= 0 for w in [alpha, beta, gamma, delta]):
            raise ValueError("Energy weights must be non-negative.")
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.config = {
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
            "delta": delta,
            **kwargs
        }

    def _calculate_complexity_energy(self, modules: List[str]) -> float:
        """
        E_complex = sum(K_approx(m_i) + H(m_i))
        """
        total_complexity_energy = 0.0
        for module_content in modules:
            # Kolmogorov complexity approximation
            k_approx = kolmogorov_approx(module_content)
            # Shannon entropy of the character distribution
            h_entropy = shannon_entropy(list(module_content))
            total_complexity_energy += k_approx + h_entropy
        return total_complexity_energy

    def _calculate_coupling_energy(self, dep_graph: Any) -> float:
        """
        E_couple = Tr(L)
        """
        # The dependency graph should be in a format that calculate_laplacian_trace can handle
        # e.g., a numpy array representing the adjacency matrix.
        return calculate_laplacian_trace(dep_graph)

    def _calculate_constraint_energy(self, constraints: List[Dict[str, Any]]) -> float:
        """
        E_cons = sum(w_k * max(0, g_k(S))^2)
        """
        total_constraint_energy = 0.0
        for constraint in constraints:
            weight = constraint.get('weight', 1.0)
            value = constraint.get('value', 0.0)
            total_constraint_energy += weight * max(0, value)**2
        return total_constraint_energy

    def _calculate_debt_energy(self, modules_metadata: List[Dict[str, Any]]) -> float:
        """
        E_debt = sum(D(m_i) * exp(-t_i / tau))
        """
        total_debt_energy = 0.0
        tau = self.config.get('debt_decay_tau', 30.0) # 30 days default
        for meta in modules_metadata:
            debt_score = meta.get('debt_score', 0.0) # Aggregated debt score
            time_since_refactor = meta.get('days_since_refactor', 0.0)
            total_debt_energy += debt_score * np.exp(-time_since_refactor / tau)
        return total_debt_energy

    def calculate_energy(self, state: QCState) -> Tuple[float, Dict[str, float]]:
        """
        Calculates the total energy of the system based on its state.
        The state object (QCState) is expected to contain all necessary information.
        """
        complexity_energy = self._calculate_complexity_energy(state.modules)
        coupling_energy = self._calculate_coupling_energy(state.dependency_graph)
        constraint_energy = self._calculate_constraint_energy(state.constraints)
        debt_energy = self._calculate_debt_energy(state.modules_metadata)

        components = {
            "complexity": complexity_energy,
            "coupling": coupling_energy,
            "constraints": constraint_energy,
            "debt": debt_energy,
        }

        total_energy = (
            self.alpha * components["complexity"]
            + self.beta * components["coupling"]
            + self.gamma * components["constraints"]
            + self.delta * components["debt"]
        )
        return total_energy, components

    def compute_gradient(self, state: QCState) -> Dict[str, float]:
        """
        A more realistic placeholder for gradient calculation.
        The gradient is proportional to the magnitude of constraint violations.
        """
        constraint_violation = sum(max(0, c.get('value', 0)) for c in state.constraints)

        # Normalize and scale the gradient factor
        factor = np.tanh(constraint_violation / 10.0)

        return {
            "complexity": self.alpha * factor,
            "coupling": self.beta * factor,
            "constraint": self.gamma * factor,
            "debt": self.delta * factor,
        }

    def gradient_norm(self, gradient: Dict[str, float]) -> float:
        return sum(v**2 for v in gradient.values())**0.5

    def descent_direction(self, gradient: Dict[str, float]) -> Dict[str, float]:
        return {k: -v for k, v in gradient.items()}
