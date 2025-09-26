"""
Lyapunov Monitor for QuantaCirc.

This module provides the LyapunovMonitor class, which is responsible for
tracking the system's Lyapunov potential and assessing its stability over time.
"""

from __future__ import annotations

from typing import List, Dict, Any
import numpy as np

from .types import QCState, LyapunovResult
from math_utils.lyapunov import (
    calculate_lyapunov_potential,
    check_bounded_excursion,
    estimate_lyapunov_exponent
)

class LyapunovMonitor:
    """
    Tracks the Lyapunov potential of the system and analyzes its stability.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the LyapunovMonitor with configuration parameters.

        Args:
            config: A dictionary containing weights and thresholds for
                    Lyapunov analysis. Expected keys: 'kappa', 'xi',
                    'excursion_max_increase', 'excursion_window_size'.
        """
        self.kappa = config.get('kappa', 10.0)  # Weight for failing tests
        self.xi = config.get('xi', 5.0)      # Weight for open obligations
        self.max_increase = config.get('excursion_max_increase', 0.1)
        self.window_size = config.get('excursion_window_size', 10)
        self.potential_history: List[float] = []

    def record_state(self, state: QCState):
        """
        Calculates and records the Lyapunov potential for the given state.
        """
        potential = calculate_lyapunov_potential(
            energy=state.energy,
            num_failing_tests=state.failing_tests,
            num_open_obligations=state.open_obligations,
            kappa=self.kappa,
            xi=self.xi
        )
        self.potential_history.append(potential)

    def check_stability(self) -> LyapunovResult:
        """
        Analyzes the history of the Lyapunov potential to check for stability.

        Returns:
            A LyapunovResult object with the stability assessment.
        """
        if len(self.potential_history) < self.window_size:
            return LyapunovResult(is_stable=True, convergence_status="Insufficient data")

        is_bounded = check_bounded_excursion(
            self.potential_history,
            self.max_increase,
            self.window_size
        )

        if not is_bounded:
            return LyapunovResult(is_stable=False, convergence_status="Diverging")

        exponent = estimate_lyapunov_exponent(np.array(self.potential_history))

        is_stable = exponent < 0
        status = "Converging" if is_stable else "Stable (not converging)"

        return LyapunovResult(
            is_stable=is_stable,
            exponent=exponent,
            convergence_status=status
        )

    def get_potential_history(self) -> List[float]:
        """
        Returns the recorded history of the Lyapunov potential.
        """
        return self.potential_history

    def reset(self):
        """
        Resets the monitor's history.
        """
        self.potential_history = []