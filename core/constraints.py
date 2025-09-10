# core/constraints.py

"""
Handles constraint validation and penalty calculation.
"""

from __future__ import annotations
from typing import List

class ConstraintValidator:
    """
    Validates system constraints and calculates penalty energy for violations.
    """

    def __init__(self, penalty_weight: float = 1.0):
        """
        Initializes the constraint validator.

        Args:
            penalty_weight: The weight for penalty calculations.
        """
        self.penalty_weight = penalty_weight

    def constraint_energy(self, state: 'QCState') -> float:
        """
        Calculates the constraint energy based on violations.
        E_constraint = Σₖ wₖ · max(0, gₖ(S))²

        For simplicity, we'll treat each violation as having a magnitude of 1.
        """
        num_violations = 0
        if hasattr(state, 'type_errors'):
            num_violations += len(state.type_errors)
        if hasattr(state, 'proof_obligations'):
            num_violations += len(state.proof_obligations)
        if hasattr(state, 'policy_violations'):
            num_violations += len(state.policy_violations)

        # Quadratic penalty
        return self.penalty_weight * (num_violations ** 2)
