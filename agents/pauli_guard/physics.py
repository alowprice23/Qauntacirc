import numpy as np
from typing import List, Tuple
from itertools import combinations
from core.types import ModuleState, OrthogonalityViolation

class PauliExclusionPrinciple:
    def __init__(self, orthogonality_threshold=1e-6):
        self.orthogonality_threshold = orthogonality_threshold

    def compute_overlap_matrix(self, modules: List[ModuleState]) -> np.ndarray:
        """Compute ⟨ψᵢ|ψⱼ⟩ for all module pairs."""
        n = len(modules)
        overlap_matrix = np.identity(n, dtype=np.float64)
        vectors = [np.array(m.state_vector, dtype=float) for m in modules]

        normalized_vectors = [v / np.linalg.norm(v) for v in vectors if np.linalg.norm(v) > 0]
        if len(normalized_vectors) != n: return overlap_matrix # Should not happen if inputs are clean

        for i, j in combinations(range(n), 2):
            overlap = np.dot(normalized_vectors[i], normalized_vectors[j])
            overlap_matrix[i, j] = overlap
            overlap_matrix[j, i] = overlap

        return overlap_matrix

    def identify_violations(self, modules: List[ModuleState], overlap_matrix: np.ndarray) -> List[OrthogonalityViolation]:
        """Identify non-orthogonal pairs based on the threshold."""
        violations = []
        for i, j in combinations(range(len(modules)), 2):
            overlap = abs(overlap_matrix[i, j])
            if overlap > self.orthogonality_threshold:
                violations.append(OrthogonalityViolation(
                    module_i=modules[i], module_j=modules[j],
                    overlap=overlap,
                    severity=overlap / self.orthogonality_threshold
                ))
        return violations

    def apply_orthogonalization(self, modules: List[ModuleState]) -> Tuple[List[ModuleState], float]:
        """
        Applies a Gram-Schmidt process to orthogonalize module vectors.
        This creates a new set of modules with orthogonal state vectors.
        """
        vectors = [np.array(m.state_vector, dtype=float) for m in modules]
        initial_ortho_metric = self.calculate_orthogonality_metric(vectors)

        orthogonal_vectors = []
        for v in vectors:
            v_ortho = v
            for u in orthogonal_vectors:
                proj = (np.dot(v, u) / np.dot(u, u)) * u
                v_ortho -= proj
            if np.linalg.norm(v_ortho) > 1e-10:
                orthogonal_vectors.append(v_ortho)

        final_ortho_metric = self.calculate_orthogonality_metric(orthogonal_vectors)
        improvement = initial_ortho_metric - final_ortho_metric

        orthogonalized_modules = [
            ModuleState(id=m.id, state_vector=v.tolist(), code=m.code)
            for m, v in zip(modules, orthogonal_vectors)
        ]
        return orthogonalized_modules, improvement

    def calculate_orthogonality_metric(self, vectors: List[np.ndarray]) -> float:
        """Calculates a metric for the system's overall orthogonality. Lower is better."""
        if len(vectors) < 2: return 0.0
        total_overlap = 0.0
        count = 0
        normalized_vectors = [v / np.linalg.norm(v) for v in vectors if np.linalg.norm(v) > 1e-10]
        for i, j in combinations(range(len(normalized_vectors)), 2):
            total_overlap += abs(np.dot(normalized_vectors[i], normalized_vectors[j]))
            count += 1
        return total_overlap / count if count > 0 else 0.0
