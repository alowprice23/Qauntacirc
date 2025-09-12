import numpy as np
from typing import List

from common.base_agent import PhysicsBasedAgent
from common.data_models import (
    ModuleState, OrthogonalizationResult, OrthogonalityViolation,
    SharedComponent, SystemState, Observable
)
from common.utils import DeduplicationEngine

class PauliGuardAgent(PhysicsBasedAgent):
    def __init__(self):
        super().__init__(
            physics_principle="Exclusion Principle",
            mathematical_formula="⟨ψᵢ|ψⱼ⟩ = 0 for i ≠ j"
        )
        self.orthogonality_threshold = 1e-6
        self.deduplication_engine = DeduplicationEngine()

    def apply_physics_principle(self, modules: List[ModuleState], **kwargs) -> OrthogonalizationResult:
        """Enforce orthogonality by eliminating overlapping code components"""
        if not modules:
            return OrthogonalizationResult(
                modules=[],
                shared_components=[],
                eliminated_duplicates=0,
                orthogonality_improvement=0.0
            )

        # Compute overlap matrix between all module pairs
        overlap_matrix = self._compute_overlap_matrix(modules)

        # Identify non-orthogonal pairs (violations of exclusion principle)
        violations = []
        for i in range(len(modules)):
            for j in range(i + 1, len(modules)):
                overlap = abs(overlap_matrix[i][j])
                if overlap > self.orthogonality_threshold:
                    violations.append(OrthogonalityViolation(
                        module_i=modules[i], module_j=modules[j],
                        overlap=overlap, severity=overlap / self.orthogonality_threshold
                    ))

        # Apply Gram-Schmidt-like orthogonalization
        orthogonalized_modules = self._apply_orthogonalization(modules, violations)

        # Generate shared components for extracted duplicates
        shared_components = self._extract_shared_components(violations)

        return OrthogonalizationResult(
            modules=orthogonalized_modules,
            shared_components=shared_components,
            eliminated_duplicates=len(violations),
            orthogonality_improvement=self._compute_orthogonality_improvement(modules, orthogonalized_modules)
        )

    def _compute_overlap_matrix(self, modules: List[ModuleState]) -> np.ndarray:
        """Compute ⟨ψᵢ|ψⱼ⟩ for all module pairs"""
        n = len(modules)
        if n == 0:
            return np.array([])
        overlap_matrix = np.zeros((n, n), dtype=complex)

        for i in range(n):
            for j in range(n):
                # Inner product in semantic space
                vec_i = modules[i].state_vector
                vec_j = modules[j].state_vector
                overlap_matrix[i][j] = np.vdot(vec_i, vec_j)

        return overlap_matrix

    def _apply_orthogonalization(self, modules: List[ModuleState], violations: List[OrthogonalityViolation]) -> List[ModuleState]:
        """Placeholder for a Gram-Schmidt-like orthogonalization process."""
        print(f"Applying mock orthogonalization for {len(violations)} violations.")
        # In a real implementation, this would modify the state vectors of the modules.
        # For this placeholder, we return the original modules unmodified.
        return modules

    def _extract_shared_components(self, violations: List[OrthogonalityViolation]) -> List[SharedComponent]:
        """Placeholder for extracting shared components from non-orthogonal modules."""
        shared_components = []
        for i, violation in enumerate(violations):
            shared_components.append(
                SharedComponent(
                    id=f"shared_{i}",
                    code=f"// Shared logic from {violation.module_i.id} & {violation.module_j.id}",
                    used_by=[violation.module_i.id, violation.module_j.id]
                )
            )
        return shared_components

    def _compute_orthogonality_improvement(self, before: List[ModuleState], after: List[ModuleState]) -> float:
        """Placeholder for computing the improvement in orthogonality."""
        # A real implementation would compare the off-diagonal elements of the overlap matrices.
        # Since our mock orthogonalization does nothing, the improvement is 0.
        return 0.0

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measure the overall system orthogonality."""
        if len(system_state.modules) < 2:
            return Observable(name="system_orthogonality", value=1.0, unit="normalized_orthogonality")

        overlap_matrix = self._compute_overlap_matrix(system_state.modules)
        # Calculate the sum of the squares of the off-diagonal elements
        off_diagonal_sum_sq = float(np.sum(np.abs(overlap_matrix - np.diag(np.diag(overlap_matrix)))**2))

        # Normalize (this is a mock metric)
        # A perfectly orthogonal system would have this be 0.
        # We can return 1 - error
        n = len(system_state.modules)
        orthogonality_metric = 1.0 - (off_diagonal_sum_sq / (n * (n - 1))) if n > 1 else 1.0

        return Observable(
            name="system_orthogonality",
            value=orthogonality_metric,
            unit="normalized_orthogonality"
        )
