# core/technical_debt.py

"""
Calculates the technical debt component of the energy function.
"""

from __future__ import annotations
import datetime
import numpy as np

class TechnicalDebtCalculator:
    """
    Calculates technical debt with a temporal aging factor.
    """

    def __init__(self, decay_constant: float, weights: dict = None):
        """
        Initializes the technical debt calculator.

        Args:
            decay_constant: A constant to control the rate of debt accumulation.
            weights: A dictionary of weights for complexity, duplication, and coverage.
        """
        self.decay_constant = decay_constant
        self.weights = weights or {
            'complexity': 1.0,
            'duplication': 1.0,
            'coverage_deficit': 1.0
        }

    def aging_factor(self, days_old: float) -> float:
        """
        Calculates a factor that increases with age.
        Using a simple linear growth model for predictability.
        Factor = 1 + (t / τ)
        """
        if self.decay_constant <= 0:
            return 1.0
        return 1.0 + (days_old / self.decay_constant)

    def calculate_debt(self, module: 'ModuleState') -> float:
        """
        Calculates the technical debt for a single module.
        D(m) = w₁·complexity + w₂·duplication + w₃·coverage_deficit
        E_debt = D(m) · (1 + t/τ)
        """
        w = self.weights

        complexity = getattr(module, 'cyclomatic_complexity', 0)
        duplication = getattr(module, 'duplication_ratio', 0)
        coverage = getattr(module, 'test_coverage', 1.0)
        coverage_deficit = 1.0 - coverage

        raw_debt = (w['complexity'] * complexity +
                    w['duplication'] * duplication +
                    w['coverage_deficit'] * coverage_deficit)

        last_modified = getattr(module, 'last_modified', datetime.datetime.now())
        days_old = (datetime.datetime.now() - last_modified).total_seconds() / (24 * 3600)

        aging = self.aging_factor(days_old)

        return raw_debt * aging
