# core/lyapunov_monitor.py

"""
Monitors the stability of the system using Lyapunov analysis.

This module provides the LyapunovMonitor class, which is responsible for
tracking the system's state trajectory and assessing its stability based on
the principles of Lyapunov stability theory.
"""

from __future__ import annotations

import numpy as np
from typing import List, Optional, Tuple

from core.types import QCState, LyapunovResult
from math_utils import lyapunov, martingales
from unittest.mock import Mock

class LyapunovFunction:
    def __init__(self, kappa: float, xi: float):
        if kappa <= 0 or xi <= 0:
            raise ValueError("Weights kappa and xi must be positive.")
        self.kappa = kappa
        self.xi = xi

    def compute(self, state: Mock) -> float:
        """Computes the Lyapunov function value."""
        # This is a mock implementation based on the test
        energy = state.energy
        failing_tests = state.failing_tests
        open_obligations = state.open_obligations
        return energy + self.kappa * failing_tests + self.xi * open_obligations

    def get_components(self, state: Mock) -> Dict[str, float]:
        """Gets the components of the Lyapunov function."""
        energy = state.energy
        test_penalty = self.kappa * state.failing_tests
        obligation_penalty = self.xi * state.open_obligations
        return {
            'energy': energy,
            'test_penalty': test_penalty,
            'obligation_penalty': obligation_penalty
        }

# Constants for stability analysis
DEFAULT_EXCURSION_BOUND = 1.5
DEFAULT_CONVERGENCE_THRESHOLD = 1e-6
MAX_HISTORY_SIZE = 1000

class LyapunovMonitor:
    """
    Monitors system stability by computing Lyapunov exponents and tracking excursions.

    The monitor maintains a history of system states (or their Lyapunov potentials)
    to analyze the trajectory's stability, convergence, and boundedness. It integrates
    with mathematical utilities for formal stability verification.
    """

    def __init__(self, excursion_bound: float = DEFAULT_EXCURSION_BOUND,
                 convergence_threshold: float = DEFAULT_CONVERGENCE_THRESHOLD):
        """
        Initializes the LyapunovMonitor.

        Args:
            excursion_bound: The maximum allowable ratio of current potential to
                             the minimum potential observed so far.
            convergence_threshold: The threshold on the Lyapunov exponent below
                                   which the system is considered converged.
        """
        self.excursion_bound = excursion_bound
        self.convergence_threshold = convergence_threshold
        self.potential_history: List[float] = []
        self.state_history: List[QCState] = []
        self.min_potential: Optional[float] = None

    def track_state(self, state: QCState):
        """
        Adds a new state to the monitor's history.

        Args:
            state: The new QCState to track.
        """
        potential = state.lyapunov_potential
        self.potential_history.append(potential)
        self.state_history.append(state)

        if len(self.potential_history) > MAX_HISTORY_SIZE:
            self.potential_history.pop(0)
            self.state_history.pop(0)

        if self.min_potential is None or potential < self.min_potential:
            self.min_potential = potential

    def track_excursion(self) -> Tuple[bool, float]:
        """
        Checks if the system state has made a significant excursion from its
        most stable point observed so far.

        An excursion occurs if the current Lyapunov potential exceeds a defined
        multiple of the minimum potential seen. This can be an indicator of

        destabilization.

        Returns:
            A tuple containing:
            - bool: True if an excursion is detected, False otherwise.
            - float: The current excursion ratio.
        """
        if self.min_potential is None or len(self.potential_history) < 1:
            return False, 0.0

        current_potential = self.potential_history[-1]

        # Avoid division by zero if min_potential is close to zero
        if abs(self.min_potential) < 1e-9:
             # If both are near zero, no excursion. If current is not, it's a large excursion.
            return (current_potential > 1e-9), float('inf') if current_potential > 1e-9 else 0.0

        excursion_ratio = current_potential / self.min_potential

        is_excursion = excursion_ratio > self.excursion_bound
        return is_excursion, excursion_ratio

    def verify_stability(self) -> LyapunovResult:
        """
        Performs a formal stability analysis on the state history.

        This method computes the Lyapunov exponent from the historical data.
        A negative exponent indicates stability, suggesting that nearby trajectories
        converge. A positive exponent indicates chaos.

        Returns:
            A LyapunovResult object summarizing the stability analysis.
        """
        if len(self.potential_history) < 2:
            return LyapunovResult(
                exponent=0.0,
                convergence_status="insufficient_data",
                iterations=len(self.potential_history)
            )

        trajectory = np.array(self.potential_history)

        # Use the lyapunov utility to compute the exponent
        exponent = lyapunov.estimate_lyapunov_exponent(trajectory)

        if exponent < -self.convergence_threshold:
            status = "stable"
        elif exponent > self.convergence_threshold:
            status = "unstable"
        else:
            status = "marginal"

        return LyapunovResult(
            exponent=exponent,
            convergence_status=status,
            iterations=len(trajectory)
        )

    def predict_convergence(self, target_potential: float) -> Optional[float]:
        """
        Estimates the time (in steps) to reach a target Lyapunov potential.

        This prediction is based on the currently observed rate of convergence,
        derived from the Lyapunov exponent.

        Args:
            target_potential: The target potential value.

        Returns:
            The estimated number of steps to convergence, or None if the system
            is not converging.
        """
        stability_result = self.verify_stability()

        # Convergence prediction is only meaningful for stable systems
        if stability_result.exponent >= 0 or len(self.potential_history) < 1:
            return None

        current_potential = self.potential_history[-1]

        # Simplified exponential decay model: P(t) = P(0) * exp(lambda * t)
        # We want to find t such that P(t) = target_potential
        # t = log(target_potential / current_potential) / lambda

        if current_potential <= target_potential:
            return 0.0

        # The exponent is the rate of convergence per step
        time_to_converge = np.log(target_potential / current_potential) / stability_result.exponent
        return time_to_converge

    def verify_martingale_property(self) -> Tuple[bool, float]:
        """
        Checks if the sequence of Lyapunov potentials behaves like a supermartingale.

        A supermartingale E[X_{t+1} | F_t] <= X_t is a process that is expected
        to decrease or stay the same over time. This is a desirable property for
        a potential function in an optimization process.

        Returns:
            A tuple containing:
            - bool: True if the supermartingale property holds, False otherwise.
            - float: The computed test statistic (e.g., drift).
        """
        if len(self.potential_history) < 10: # Need some data to test
            return True, 0.0 # Assume property holds if not enough data

        trajectory = np.array(self.potential_history)

        # Use the martingale utility to check the property
        is_supermartingale, drift = martingales.is_supermartingale(trajectory)

        return is_supermartingale, drift

    def reset(self):
        """
        Resets the monitor's history.
        """
        self.potential_history.clear()
        self.state_history.clear()
        self.min_potential = None
