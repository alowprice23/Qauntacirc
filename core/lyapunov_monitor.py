# core/lyapunov_monitor.py

from typing import List, Tuple
import numpy as np
from core.types import QCState, LyapunovResult
from core.lyapunov_function import LyapunovFunction

class LyapunovMonitor:
    """
    A class to monitor the Lyapunov stability of the system.
    """
    def __init__(self, lyapunov_function: LyapunovFunction, excursion_bound: float = 1.5, convergence_threshold: float = 1e-4, min_history_for_stability: int = 10):
        self.lyapunov_function = lyapunov_function
        self.excursion_bound = excursion_bound
        self.convergence_threshold = convergence_threshold
        self.min_history_for_stability = min_history_for_stability
        self.potential_history: List[float] = []
        self.state_history: List[QCState] = []
        self.min_potential: float | None = None

    def reset(self):
        self.potential_history = []
        self.state_history = []
        self.min_potential = None

    def track_state(self, state: QCState):
        potential = self.lyapunov_function.compute(state)
        state.lyapunov_potential = potential
        self.potential_history.append(potential)
        self.state_history.append(state)
        if self.min_potential is None or potential < self.min_potential:
            self.min_potential = potential

    def track_excursion(self) -> Tuple[bool, float]:
        if not self.potential_history or self.min_potential is None:
            return False, 0.0

        ratio = self.potential_history[-1] / self.min_potential
        return ratio > self.excursion_bound, ratio

    def verify_stability(self) -> LyapunovResult:
        if len(self.potential_history) < self.min_history_for_stability:
            return LyapunovResult(is_stable=False, convergence_status="insufficient_data", exponent=0.0, iterations=len(self.potential_history))

        positive_potentials = np.array([p for p in self.potential_history if p > 0])
        if len(positive_potentials) < self.min_history_for_stability:
            return LyapunovResult(is_stable=False, convergence_status="insufficient_data", exponent=0.0, iterations=len(self.potential_history))

        log_potentials = np.log(positive_potentials)
        time_steps = np.arange(len(log_potentials))
        try:
            # Fit a line to the log of the potentials
            coeffs = np.polyfit(time_steps, log_potentials, 1)
            exponent = coeffs[0]
        except np.linalg.LinAlgError:
            exponent = 0.0

        if exponent < -self.convergence_threshold:
            status = "stable"
        elif exponent > self.convergence_threshold:
            status = "unstable"
        else:
            status = "marginal"

        return LyapunovResult(
            is_stable=status == "stable",
            convergence_status=status,
            exponent=exponent,
            iterations=len(self.potential_history)
        )

    def predict_convergence(self, target_potential: float) -> float | None:
        stability_result = self.verify_stability()
        if not stability_result.is_stable or stability_result.exponent >= 0:
            return None

        current_potential = self.potential_history[-1]
        if current_potential <= target_potential:
            return 0.0

        # V(t) = V0 * exp(lambda * t)
        # log(V(t)/V0) = lambda * t
        # t = log(V(t)/V0) / lambda
        time_to_converge = np.log(target_potential / current_potential) / stability_result.exponent
        return time_to_converge

    def verify_martingale_property(self) -> Tuple[bool, float]:
        if len(self.potential_history) < 2:
            return True, 0.0 # Not enough data to say otherwise

        diffs = np.diff(self.potential_history)
        drift = np.mean(diffs)

        # Supermartingale: E[X_{n+1} | F_n] <= X_n
        # We check the average drift
        return drift <= 0, drift
