from __future__ import annotations
import datetime
from math_utils.kolmogorov_bounds import normalized_compression_distance

class TechnicalDebtAnalyzer:
    """
    Analyzes technical debt based on cyclomatic complexity, code duplication,
    and test coverage.
    """
    def __init__(self, weights: dict = None):
        self.weights = weights or {
            'complexity': 1.0,
            'duplication': 1.0,
            'coverage_deficit': 1.0
        }

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        Calculates cyclomatic complexity using the radon library.
        """
        from radon.visitors import ComplexityVisitor
        try:
            visitor = ComplexityVisitor.from_code(code)
            # For a single module, we can take the average complexity.
            # A more sophisticated approach might look at the max complexity
            # or a weighted sum.
            if not visitor.functions:
                return 1 # A module with no functions has a complexity of 1.
            return sum(f.complexity for f in visitor.functions)
        except Exception:
            # If radon fails to parse, return a high complexity as a penalty.
            return 25

    def _calculate_code_duplication(self, module_a_code: str, module_b_code: str) -> float:
        """
        Calculates code duplication using Normalized Compression Distance.
        """
        return normalized_compression_distance(module_a_code, module_b_code)

    def analyze_module_debt(self, module: 'ModuleState', all_modules: list['ModuleState']) -> float:
        """
        Analyzes the technical debt for a single module.
        """
        w = self.weights

        # Cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(module.code)

        # Code duplication
        total_duplication = 0.0
        if len(all_modules) > 1:
            for other_module in all_modules:
                if module.id != other_module.id:
                    total_duplication += self._calculate_code_duplication(module.code, other_module.code)
            duplication = total_duplication / (len(all_modules) - 1)
        else:
            duplication = 0.0

        # Test coverage deficit
        coverage = getattr(module, 'test_coverage', 1.0)
        coverage_deficit = 1.0 - coverage

        debt_score = (w['complexity'] * complexity +
                      w['duplication'] * duplication +
                      w['coverage_deficit'] * coverage_deficit)

        return debt_score
