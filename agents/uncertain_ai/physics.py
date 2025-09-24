import numpy as np
import math
from collections import Counter
from core.types import SystemState, Module

class UncertaintyPrinciple:
    def __init__(self, hbar_effective=1.0):
        self.hbar_effective = hbar_effective

    def measure_specification_uncertainty(self, state: SystemState) -> float:
        """Measure uncertainty in specifications (Δx) via Shannon entropy."""
        if not state.requirements:
            return 0.0
        entropies = [self.calculate_shannon_entropy(req) for req in state.requirements]
        return np.std(entropies) if entropies else 0.0

    def measure_implementation_uncertainty(self, state: SystemState) -> float:
        """Measure uncertainty in implementation (Δp) via a composite metric."""
        if not state.modules:
            return 0.0
        entropies = [self.calculate_module_entropy(mod) for mod in state.modules]
        return np.std(entropies) if entropies else 0.0

    def calculate_shannon_entropy(self, text: str) -> float:
        """Calculates the Shannon entropy of a string."""
        if not text:
            return 0.0
        counts = Counter(text)
        total_len = len(text)
        return -sum((count / total_len) * math.log2(count / total_len) for count in counts.values())

    def calculate_module_entropy(self, module: Module) -> float:
        """Calculates a composite entropy for a module."""
        norm_complexity = module.cyclomatic_complexity / 50.0
        norm_duplication = module.duplication_factor
        token_entropy = self.calculate_shannon_entropy(" ".join(module.semantic_tokens))
        norm_token_entropy = token_entropy / 10.0

        return 0.4 * norm_complexity + 0.4 * norm_duplication + 0.2 * norm_token_entropy
