import math
import numpy as np
import gzip
import bz2
import lzma
from datetime import datetime
from typing import Dict

from core.types import SystemState, EnergyBreakdown, Module

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

    def _compress_gzip(self, data: bytes) -> int:
        return len(gzip.compress(data))

    def _compress_bzip2(self, data: bytes) -> int:
        return len(bz2.compress(data))

    def _compress_lzma(self, data: bytes) -> int:
        return len(lzma.compress(data))

    def _compute_shannon_entropy(self, tokens: list[str]) -> float:
        if not tokens:
            return 0.0

        freq_map = {}
        for token in tokens:
            freq_map[token] = freq_map.get(token, 0) + 1

        entropy = 0.0
        total_tokens = len(tokens)
        for token in freq_map:
            prob = freq_map[token] / total_tokens
            entropy -= prob * math.log2(prob)

        return entropy

    def _compute_complexity_energy(self, state: SystemState) -> float:
        """E_complexity = Σᵢ [K_approx(mᵢ) + H(mᵢ)]"""
        total_complexity = 0.0
        for module in state.modules:
            # Kolmogorov approximation using multi-compressor approach
            k_approx = min(
                self._compress_gzip(module.normalized_ast),
                self._compress_bzip2(module.normalized_ast),
                self._compress_lzma(module.normalized_ast)
            )

            # Shannon entropy of semantic tokens
            h_entropy = self._compute_shannon_entropy(module.semantic_tokens)

            total_complexity += k_approx + h_entropy

        return total_complexity

    def _compute_coupling_energy(self, state: SystemState) -> float:
        """E_coupling = Tr(L) where L is the dependency graph Laplacian"""
        if state.dependency_graph is None or state.dependency_graph.adjacency_matrix is None:
            return 0.0

        adjacency_matrix = np.array(state.dependency_graph.adjacency_matrix)
        if adjacency_matrix.size == 0:
            return 0.0

        # Degree matrix is a diagonal matrix of vertex degrees
        degrees = np.sum(adjacency_matrix, axis=1)
        degree_matrix = np.diag(degrees)

        # Laplacian matrix L = D - A
        laplacian = degree_matrix - adjacency_matrix

        # Trace of the Laplacian is the sum of its eigenvalues
        eigenvalues = np.linalg.eigvals(laplacian)
        return float(np.sum(eigenvalues.real))

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
