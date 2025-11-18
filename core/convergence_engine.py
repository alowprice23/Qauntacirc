# core/convergence_engine.py

"""
Determines if the system has reached a stable, converged state.

This module provides a set of criteria and a comprehensive engine to assess
whether the optimization process has concluded, based on various signals
from the system's state and history.
"""

from __future__ import annotations

from typing import List, Dict, Any
import numpy as np

from core.types import QCState
from core.lyapunov_monitor import LyapunovMonitor
from core.two_phase_annealer import TwoPhaseAnnealer

class ConvergenceCriteria:
    """
    A container for different convergence criteria settings.
    """
    def __init__(self,
                 energy_variance_threshold: float = 1e-8,
                 lyapunov_exponent_threshold: float = -1e-6,
                 potential_drift_threshold: float = 1e-7,
                 window_size: int = 50):
        """
        Initializes the convergence criteria.

        Args:
            energy_variance_threshold: The maximum variance in energy over a
                                     window for the system to be considered stable.
            lyapunov_exponent_threshold: The system's Lyapunov exponent must be
                                         below this value (i.e., negative).
            potential_drift_threshold: The maximum average change (drift) in
                                       Lyapunov potential over a window.
            window_size: The number of recent states to consider for evaluation.
        """
        self.energy_variance_threshold = energy_variance_threshold
        self.lyapunov_exponent_threshold = lyapunov_exponent_threshold
        self.potential_drift_threshold = potential_drift_threshold
        self.window_size = window_size

class ConvergenceEngine:
    """
    Evaluates system state history to check for convergence.

    The engine uses multiple criteria to provide a robust assessment of convergence,
    avoiding premature termination of the optimization process.
    """

    def __init__(self, criteria: ConvergenceCriteria = None):
        """
        Initializes the ConvergenceEngine.

        Args:
            criteria: An object containing the thresholds for convergence checks.
        """
        self.criteria = criteria or ConvergenceCriteria()

    def check_convergence(self,
                          state_history: List[QCState],
                          lyapunov_monitor: LyapunovMonitor,
                          annealer: TwoPhaseAnnealer) -> Dict[str, Any]:
        """
        Performs a comprehensive check for convergence.

        Args:
            state_history: A list of recent QCStates.
            lyapunov_monitor: The system's Lyapunov monitor.
            annealer: The system's annealer.

        Returns:
            A dictionary containing the overall convergence status and the
            status of individual checks.
        """
        if len(state_history) < self.criteria.window_size:
            return {"converged": False, "reason": "Insufficient history"}

        recent_states = state_history[-self.criteria.window_size:]

        # 1. Check if the annealer itself thinks it's done
        annealer_finished = annealer.is_finished
        if annealer_finished:
            return {
                "converged": True,
                "reason": "Annealer finished temperature schedule.",
                "annealer_finished": True
            }

        # 2. Check for energy stability
        energy_stable, energy_variance = self._check_energy_stability(recent_states)

        # 3. Check Lyapunov exponent for stability
        lyapunov_stable, lyapunov_exponent = self._check_lyapunov_stability(lyapunov_monitor)

        # 4. Check for low drift in Lyapunov potential
        potential_stable, potential_drift = self._check_potential_drift(recent_states)

        # 5. Check contractive mapping property from annealer
        contractive_converged = annealer.check_convergence(recent_states)

        # Overall convergence is a combination of these factors
        # A conservative approach: require multiple signals to agree.
        converged = (
            energy_stable and
            lyapunov_stable and
            potential_stable and
            contractive_converged and
            annealer.phase == "B"  # Should be in exploitation phase
        )

        return {
            "converged": converged,
            "reason": "Converged based on multiple stability criteria." if converged else "Not yet converged.",
            "checks": {
                "energy_stability": {"succeeded": energy_stable, "variance": energy_variance},
                "lyapunov_stability": {"succeeded": lyapunov_stable, "exponent": lyapunov_exponent},
                "potential_stability": {"succeeded": potential_stable, "drift": potential_drift},
                "contractive_mapping": {"succeeded": contractive_converged},
                "in_exploitation_phase": annealer.phase == "B"
            }
        }

    def _check_energy_stability(self, recent_states: List[QCState]) -> tuple[bool, float]:
        """Checks if the energy has stabilized over the recent window."""
        energies = [s.energy for s in recent_states]
        variance = np.var(energies)
        is_stable = variance < self.criteria.energy_variance_threshold
        return is_stable, variance

    def _check_lyapunov_stability(self, lyapunov_monitor: LyapunovMonitor) -> tuple[bool, float]:
        """Checks if the Lyapunov exponent indicates stability."""
        result = lyapunov_monitor.verify_stability()
        is_stable = result.exponent < self.criteria.lyapunov_exponent_threshold
        return is_stable, result.exponent

    def _check_potential_drift(self, recent_states: List[QCState]) -> tuple[bool, float]:
        """Checks if the Lyapunov potential is no longer decreasing significantly."""
        potentials = [s.lyapunov_potential for s in recent_states]
        # Calculate the average change (drift)
        drift = np.mean(np.diff(potentials))
        is_stable = abs(drift) < self.criteria.potential_drift_threshold
        return is_stable, drift

# Example Usage
if __name__ == '__main__':
    # This is a conceptual example. A real test would require mock objects
    # for the annealer and monitor, and a realistic history of states.

    engine = ConvergenceEngine()
    print("ConvergenceEngine initialized with default criteria:")
    print(f"  Energy variance threshold: {engine.criteria.energy_variance_threshold}")
    print(f"  Lyapunov exponent threshold: {engine.criteria.lyapunov_exponent_threshold}")
    print(f"  Potential drift threshold: {engine.criteria.potential_drift_threshold}")
    print(f"  Window size: {engine.criteria.window_size}")

    # To run a check, you would need to populate state_history and mock objects
    # e.g., result = engine.check_convergence(history, mock_monitor, mock_annealer)
    # print(result)
