import numpy as np
from scipy.linalg import expm, norm
from scipy.sparse import csr_matrix
from typing import Dict, Any, Tuple, Optional
from core.data_models import CanonicalAST, DensityMatrix, SystemState, Module, QuantumState
# from math_utils.graph_spectra import compute_laplacian_spectrum
# from math_utils.dim_analysis import extract_semantic_features
import networkx as nx
from core.energy_calculator import EnergyCalculator
from math_utils.laplacian import get_normalized_laplacian as compute_normalized_laplacian


class Functor:
    """
    A class that encapsulates the functorial mapping from software
    systems to quantum systems.
    """

    def __init__(self, beta: float = 0.1, energy_weights: Optional[Dict[str, float]] = None):
        self.beta = beta
        if energy_weights is None:
            self.energy_weights = {'alpha': 1.0, 'beta': 1.0, 'gamma': 1.0, 'delta': 1.0}
        else:
            self.energy_weights = energy_weights
        self.energy_calculator = EnergyCalculator(**self.energy_weights)

    def _compute_cyclomatic_complexity(self, canonical_ast: CanonicalAST) -> int:
        from radon.visitors import ComplexityVisitor
        try:
            code = canonical_ast.normalized_ast.decode('utf-8')
            visitor = ComplexityVisitor.from_code(code)
            total_complexity = 0
            if visitor.functions:
                total_complexity = sum(f.complexity for f in visitor.functions)
            return total_complexity
        except Exception:
            return 1

    def _compute_cognitive_complexity(self, canonical_ast: CanonicalAST) -> int:
        import cognitive_complexity.api as cc
        try:
            code = canonical_ast.normalized_ast.decode('utf-8')
            results = cc.get_cognitive_complexity(code)
            total_complexity = 0
            if results:
                total_complexity = sum(r.complexity for r in results)
            return total_complexity
        except Exception:
            return 1

    def _compute_max_nesting_depth(self, canonical_ast: CanonicalAST) -> int:
        return 1 # Placeholder

    def _analyze_def_use_patterns(self, canonical_ast: CanonicalAST) -> int:
        return 1 # Placeholder

    def _compute_aliasing_complexity(self, canonical_ast: CanonicalAST) -> int:
        return 1 # Placeholder

    def _analyze_memory_patterns(self, canonical_ast: CanonicalAST) -> int:
        return 1 # Placeholder

    def _count_type_constraints(self, canonical_ast: CanonicalAST) -> int:
        return 1 # Placeholder

    def _measure_polymorphic_usage(self, canonical_ast: CanonicalAST) -> int:
        return 1 # Placeholder

    def _count_variance_annotations(self, canonical_ast: CanonicalAST) -> int:
        return 1 # Placeholder

    def _measure_interface_surface(self, canonical_ast: CanonicalAST) -> int:
        return 1 # Placeholder

    def _count_contract_annotations(self, canonical_ast: CanonicalAST) -> int:
        return 1 # Placeholder

    def extract_features(self, canonical_ast: CanonicalAST) -> np.ndarray:
        """
        Extract semantic features preserving program structure:
        - Control flow complexity (cyclomatic, cognitive)
        - Data flow patterns (def-use chains, aliasing)
        - Type system features (polymorphism, constraints)
        - Interface signatures (contracts, pre/post conditions)
        - Structural metrics (depth, branching, modularity)
        """
        features = {}

        # Control/complexity features
        features['cyclomatic'] = self._compute_cyclomatic_complexity(canonical_ast)
        features['cognitive'] = self._compute_cognitive_complexity(canonical_ast)
        features['nesting_depth'] = self._compute_max_nesting_depth(canonical_ast)

        # Data dependency features
        features['def_use_chains'] = self._analyze_def_use_patterns(canonical_ast)
        features['aliasing_factor'] = self._compute_aliasing_complexity(canonical_ast)
        features['memory_access'] = self._analyze_memory_patterns(canonical_ast)

        # Type system features
        features['type_constraints'] = self._count_type_constraints(canonical_ast)
        features['polymorphism'] = self._measure_polymorphic_usage(canonical_ast)
        features['variance_markers'] = self._count_variance_annotations(canonical_ast)

        # Interface and contract features
        features['interface_complexity'] = self._measure_interface_surface(canonical_ast)
        features['contract_density'] = self._count_contract_annotations(canonical_ast)

        return np.array(list(features.values()), dtype=np.float64)

    def features_to_hermitian(self, features: np.ndarray,
                             coupling_graph: Optional[csr_matrix] = None) -> np.ndarray:
        """
        Construct positive semidefinite Hermitian matrix from features:
        H = Φ Φᵀ + β L̃
        where Φ stacks feature blocks and L̃ is normalized Laplacian
        """
        # Create feature embedding matrix
        d = len(features)
        phi_matrix = np.outer(features, features)  # Rank-1 matrix Φ Φᵀ

        # Add graph structure if available
        if coupling_graph is not None:
            # Normalized Laplacian: L̃ = D^(-1/2) L D^(-1/2)
            laplacian_norm = compute_normalized_laplacian(coupling_graph)
            # Ensure same dimensions
            if laplacian_norm.shape[0] == d:
                phi_matrix += 0.1 * laplacian_norm.toarray()

        # Ensure Hermitian and PSD
        hermitian = (phi_matrix + phi_matrix.T) / 2
        eigenvals, eigenvecs = np.linalg.eigh(hermitian)
        if np.min(eigenvals) < -1e-10:  # Numerical tolerance
            # Project to PSD cone
            eigenvals = np.maximum(eigenvals, 0)
            hermitian = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T.conj()

        return hermitian

    def hermitian_to_density_matrix(self, H: np.ndarray) -> DensityMatrix:
        """
        Construct normalized density matrix via matrix exponential:
        ρ = exp(-H) / Tr(exp(-H))

        Uses scaling and squaring for numerical stability
        """
        # Scale matrix for numerical stability
        max_eigenval = np.max(np.real(np.linalg.eigvals(H)))
        if max_eigenval > 10:  # Scale down large eigenvalues
            H_scaled = H / (max_eigenval / 10)
        else:
            H_scaled = H

        # Matrix exponential with error control
        exp_neg_H = expm(-H_scaled)

        # Normalize to unit trace
        trace_val = np.trace(exp_neg_H)
        if abs(trace_val) < 1e-12:
            raise ValueError("Matrix exponential has zero trace - numerical instability")

        rho = exp_neg_H / trace_val

        # Verify density matrix properties
        assert abs(np.trace(rho) - 1.0) < 1e-10, "Trace normalization failed"
        eigenvals = np.linalg.eigvals(rho)
        assert all(np.real(ev) >= -1e-10 for ev in eigenvals), "Non-positive eigenvalues"

        return DensityMatrix(matrix=rho, dimension=H.shape[0])

    def map_software_to_quantum(self, state: SystemState) -> QuantumState:
        """
        The main functor F that maps a software state to a density matrix.
        This is the primary method of the functor.

        Args:
            state: The software state to map.

        Returns:
            A QuantumState object representing the quantum state of the software.
        """
        # For now, we'll just use the first module.
        # A more sophisticated approach would be to aggregate features from all modules.
        if not state.modules:
            raise ValueError("SystemState has no modules to analyze.")

        canonical_ast = state.modules[0]
        features = self.extract_features(canonical_ast)

        coupling_graph = None
        if state.dependency_graph and state.dependency_graph.adjacency_matrix:
            coupling_graph = csr_matrix(state.dependency_graph.adjacency_matrix)

        H = self.features_to_hermitian(features, coupling_graph)
        rho = self.hermitian_to_density_matrix(H)

        return QuantumState(
            density_matrix=rho,
        )
