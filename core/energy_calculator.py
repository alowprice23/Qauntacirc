import math
import numpy as np
from datetime import datetime
from typing import Dict

from core.data_models import SystemState, EnergyBreakdown, Module
from math_utils.info_entropy import shannon_entropy
from math_utils.kolmogorov_bounds import multi_compressor_bound
from math_utils.laplacian import get_normalized_laplacian

class EnergyCalculator:
    def __init__(self, alpha: float, beta: float, gamma: float, delta: float, tau: float = 3.154e+7):
        """
        Initializes the EnergyCalculator with weights for the energy components.
        τ (tau) is the decay constant for technical debt in seconds. Default is 1 year.
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.tau = tau

    def compute_total_energy(self, state: SystemState) -> EnergyBreakdown:
        """Compute E_approx = α·E_complexity + β·E_coupling + γ·E_constraint + δ·E_debt"""
        complexity = self._compute_complexity_energy(state)
        coupling = self._compute_coupling_energy(state)
        constraint = self._compute_constraint_energy(state)
        debt = self._compute_technical_debt_energy(state)

        total = self.alpha * complexity + self.beta * coupling + self.gamma * constraint + self.delta * debt
        return EnergyBreakdown(total=total, complexity=complexity, coupling=coupling,
                               constraint=constraint, debt=debt)

    def calculate_energy(self, state: SystemState) -> tuple[float, dict[str, float]]:
        """Calculates the total energy and returns it along with its components."""
        breakdown = self.compute_total_energy(state)
        components = {
            "complexity": breakdown.complexity,
            "coupling": breakdown.coupling,
            "constraint": breakdown.constraint,
            "debt": breakdown.debt,
        }
        return breakdown.total, components

    def compute_gradient(self, state: SystemState) -> dict[str, float]:
        """
        Computes the gradient of the energy function with respect to the weights.
        For a linear energy function E = α*c + β*o + γ*n + δ*d, the partial derivatives
        ∂E/∂α, ∂E/∂β, etc., are simply the component energy values.
        This method is a conceptual placeholder for a more complex gradient calculation
        that would be needed for state-based optimization.
        """
        breakdown = self.compute_total_energy(state)
        return {
            'alpha': breakdown.complexity,
            'beta': breakdown.coupling,
            'gamma': breakdown.constraint,
            'delta': breakdown.debt,
        }

    def _compute_complexity_energy(self, state: SystemState) -> float:
        """E_complexity = Σᵢ [K_approx(mᵢ) + H(mᵢ)]"""
        total_complexity = 0.0
        for module in state.modules:
            # Multi-compressor Kolmogorov approximation
            k_approx = multi_compressor_bound(module.normalized_ast)
            # Shannon entropy of semantic tokens
            h_tokens = shannon_entropy(module.semantic_tokens)
            total_complexity += k_approx + h_tokens
        return total_complexity

    def _compute_coupling_energy(self, state: SystemState) -> float:
        """E_coupling = Tr(L) where L is the normalized graph Laplacian"""
        if state.dependency_graph is None or not state.dependency_graph.adjacency_matrix:
            return 0.0

        adjacency_matrix = np.array(state.dependency_graph.adjacency_matrix)
        if adjacency_matrix.size == 0:
            return 0.0

        # Use the normalized Laplacian as required
        laplacian = get_normalized_laplacian(adjacency_matrix)

        # The trace of the Laplacian is the sum of its eigenvalues.
        # It's more efficient to compute the trace directly from the matrix.
        return np.real(np.trace(laplacian))

    def _compute_constraint_energy(self, state: SystemState) -> float:
        """E_constraint = Σₖ wₖ·max(0, gₖ(S))²"""
        total_penalty = 0.0
        for constraint in state.constraints:
            violation = max(0.0, constraint.evaluate_violation(state))
            penalty = constraint.weight * (violation ** 2)
            total_penalty += penalty

        return total_penalty

    def _compute_technical_debt_energy(self, state: SystemState) -> float:
        """E_debt = Σᵢ D(mᵢ)·e^(-t_i/τ)"""
        total_debt = 0.0
        current_time = datetime.now()

        for module in state.modules:
            debt_score = (module.cyclomatic_complexity +
                           module.duplication_factor +
                           module.coverage_deficit)

            time_since_refactor = (current_time - module.last_refactor).total_seconds()
            if time_since_refactor < 0:
                time_since_refactor = 0

            decay_factor = math.exp(-time_since_refactor / self.tau)

            total_debt += debt_score * decay_factor

        return total_debt
