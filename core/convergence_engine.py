# core/convergence_engine.py

"""
Determines if the system has reached a stable, converged state.
"""

from __future__ import annotations

from typing import List, Dict, Any
import numpy as np

from .types import QCState
from .lyapunov_monitor import LyapunovMonitor
from .two_phase_annealer import TwoPhaseAnnealer
from math_utils.pl_inequality import validate_linear_convergence

class ConvergenceCriteria:
    """
    A container for different convergence criteria settings.
    """
    def __init__(self,
                 energy_variance_threshold: float = 1e-8,
                 window_size: int = 50,
                 pl_mu: float = 0.1,
                 pl_step_size: float = 0.1):
        self.energy_variance_threshold = energy_variance_threshold
        self.window_size = window_size
        self.pl_mu = pl_mu
        self.pl_step_size = pl_step_size

class ConvergenceEngine:
    """
    Evaluates system state history to check for convergence.
    """

    def __init__(self, criteria: ConvergenceCriteria = None):
        self.criteria = criteria or ConvergenceCriteria()

    def check_convergence(self,
                          state_history: List[QCState],
                          lyapunov_monitor: LyapunovMonitor,
                          annealer: TwoPhaseAnnealer) -> Dict[str, Any]:
        """
        Performs a comprehensive check for convergence.
        """
        if len(state_history) < self.criteria.window_size:
            return {"converged": False, "reason": "Insufficient history"}

        recent_states = state_history[-self.criteria.window_size:]

        # 1. Check if the annealer has converged
        annealer_converged = annealer.check_convergence()

        # 2. Check for energy stability
        energy_stable, energy_variance = self._check_energy_stability(recent_states)

        # 3. Check Lyapunov stability
        lyapunov_result = lyapunov_monitor.check_stability()
        lyapunov_stable = lyapunov_result.is_stable

        # 4. Check for PL-based linear convergence
        pl_converged = self._check_pl_convergence(recent_states)

        converged = (
            annealer_converged and
            energy_stable and
            lyapunov_stable and
            pl_converged and
            annealer.phase == "B"
        )

        return {
            "converged": converged,
            "reason": "Converged based on multiple stability criteria." if converged else "Not yet converged.",
            "checks": {
                "annealer_convergence": {"succeeded": annealer_converged},
                "energy_stability": {"succeeded": energy_stable, "variance": energy_variance},
                "lyapunov_stability": {"succeeded": lyapunov_stable, "details": lyapunov_result.dict()},
                "pl_linear_convergence": {"succeeded": pl_converged},
                "in_exploitation_phase": annealer.phase == "B"
            }
        }

    def _check_energy_stability(self, recent_states: List[QCState]) -> tuple[bool, float]:
        """Checks if the energy has stabilized over the recent window."""
        energies = [s.energy for s in recent_states]
        variance = np.var(energies)
        is_stable = variance < self.criteria.energy_variance_threshold
        return is_stable, variance

    def _check_pl_convergence(self, recent_states: List[QCState]) -> bool:
        """
        Checks if the energy sequence demonstrates linear convergence consistent
        with the Polyak-Łojasiewicz inequality.
        """
        energy_sequence = [s.energy for s in recent_states]
        e_star = min(energy_sequence)  # Estimate optimal energy in the window

        return validate_linear_convergence(
            energy_sequence=energy_sequence,
            e_star=e_star,
            mu=self.criteria.pl_mu,
            step_size=self.criteria.pl_step_size
        )
