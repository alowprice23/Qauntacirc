from typing import List
from core.data_models import SystemState, LyapunovMetrics, ObligationStatus

class LyapunovMonitor:
    """
    Monitors the system's Lyapunov potential to ensure stability.
    The Lyapunov function is defined as:
    Φ(S) = E_approx(S) + κ·#{failing tests} + ξ·#{open obligations}
    """
    def __init__(self, kappa: float, xi: float):
        """
        Initializes the monitor with penalty coefficients.
        Args:
            kappa (float): Weight for the penalty on failing tests.
            xi (float): Weight for the penalty on open obligations.
        """
        if kappa < 0 or xi < 0:
            raise ValueError("Lyapunov penalty coefficients must be non-negative.")
        self.kappa = kappa
        self.xi = xi
        self.history: List[LyapunovMetrics] = []

    def compute(self, state: SystemState) -> LyapunovMetrics:
        """
        Computes the Lyapunov potential for a given system state.
        """
        energy = state.energy_breakdown.total
        test_failures = len(state.failing_tests)
        open_obligations = len([
            ob for ob in state.obligations if ob.status != ObligationStatus.CLOSED
        ])

        test_penalty = self.kappa * test_failures
        obligation_penalty = self.xi * open_obligations

        phi = energy + test_penalty + obligation_penalty

        metrics = LyapunovMetrics(
            phi=phi,
            energy=energy,
            test_penalty=test_penalty,
            obligation_penalty=obligation_penalty
        )
        return metrics

    def track(self, metrics: LyapunovMetrics):
        """Adds the latest Lyapunov metrics to the history."""
        self.history.append(metrics)

    def verify_descent(self) -> bool:
        """
        Checks if the potential has not increased in the last step (is non-increasing).
        A true supermartingale property would require E[Φ(k+1)|F_k] <= Φ(k).
        This is a simpler, deterministic check.
        """
        if len(self.history) < 2:
            return True # Not enough data to say otherwise
        return self.history[-1].phi <= self.history[-2].phi
