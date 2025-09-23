import math
import numpy as np
from datetime import datetime
from typing import Dict
import networkx as nx

from core.types import SystemState, EnergyBreakdown, Module
from math_utils.kolmogorov_bounds import KolmogorovApproximator
from math_utils.info_entropy import shannon_entropy
from math_utils.laplacian_analyzer import LaplacianAnalyzer
from math_utils.graph_spectra import SpectralAnalysis
from core.constraint_solver import ConstraintValidator
from core.technical_debt import TechnicalDebtAnalyzer

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
        self.kolmogorov_approximator = KolmogorovApproximator()

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
        """
        Implement: E_complex = Σᵢ [K_approx(mᵢ) + H(mᵢ)]

        REQUIREMENTS:
        - K_approx using multi-compressor (gzip, bzip2, lzma) per README Part 1.2.1
        - Shannon entropy H(mᵢ) calculation per math_utils/info_entropy.py
        - Bennett-Gács deviation bounds validation

        IMPORTS REQUIRED:
        from math_utils.kolmogorov_bounds import KolmogorovApproximator
        from math_utils.info_entropy import shannon_entropy
        from compression import MultiCompressor
        """
        total_complexity = 0.0
        for module in state.modules:
            # Kolmogorov approximation using multi-compressor approach
            k_approx = self.kolmogorov_approximator.approximate(module.normalized_ast)

            # Shannon entropy of semantic tokens
            h_entropy = shannon_entropy(module.semantic_tokens)

            total_complexity += k_approx + h_entropy

        return total_complexity

    def _compute_coupling_energy(self, state: SystemState) -> float:
        """
        Implement: E_couple = Tr(L) = Σᵢ λᵢ(L) where L = D - A

        REQUIREMENTS:
        - Graph Laplacian computation per math_utils/laplacian.py
        - Spectral analysis for eigenvalues per math_utils/graph_spectra.py
        - Fiedler value calculation for connectivity

        IMPORTS REQUIRED:
        from math_utils.laplacian import LaplacianAnalyzer
        from math_utils.graph_spectra import SpectralAnalysis
        import networkx as nx
        """
        if state.dependency_graph is None or not state.dependency_graph.nodes():
            return 0.0

        laplacian_analyzer = LaplacianAnalyzer(state.dependency_graph)
        laplacian_matrix = laplacian_analyzer.laplacian_matrix()

        # The coupling energy is the trace of the Laplacian
        coupling_energy = float(np.trace(laplacian_matrix))

        # We also perform spectral analysis for connectivity insights
        spectral_analyzer = SpectralAnalysis(laplacian_matrix)
        fiedler_value = spectral_analyzer.get_fiedler_value()

        # The Fiedler value is not directly part of the energy, but is a crucial metric
        # that can be used for other analyses (e.g., by agents).
        # We can store it in the state or log it if needed.
        # For now, we just calculate it as required.

        return coupling_energy

    def _compute_constraint_energy(self, state: SystemState) -> float:
        """
        Implement: E_cons = Σₖ wₖ · max(0, gₖ(S))²

        REQUIREMENTS:
        - Quadratic penalty functions for violations
        - Type safety constraint validation
        - Proof obligation tracking per core/types.py
        - SMT constraint validation integration

        IMPORTS REQUIRED:
        from core.constraint_solver import ConstraintValidator
        from proofs.validators import ProofObligationTracker
        """
        # Assuming SMT solver is used for some constraints
        validator = ConstraintValidator(use_smt_solver=True)
        return validator.validate_and_compute_energy(state)

    def _compute_technical_debt_energy(self, state: SystemState) -> float:
        """
        Implement: E_debt = Σᵢ D(mᵢ) · e^(-tᵢ/τ)

        REQUIREMENTS:
        - Cyclomatic complexity calculation
        - Code duplication detection using NCD
        - Test coverage deficit measurement
        - Temporal decay with configurable τ

        IMPORTS REQUIRED:
        from core.technical_debt import TechnicalDebtAnalyzer
        from math_utils.distance_metrics import normalized_compression_distance
        """
        debt_analyzer = TechnicalDebtAnalyzer()
        total_debt_energy = 0.0
        current_time = datetime.now()

        for module in state.modules:
            debt_score = debt_analyzer.analyze_module_debt(module, state.modules)

            time_since_refactor = (current_time - module.last_refactor).total_seconds()
            if time_since_refactor < 0:
                time_since_refactor = 0

            decay_factor = math.exp(-time_since_refactor / self.tau)

            total_debt_energy += debt_score * decay_factor

        return total_debt_energy
