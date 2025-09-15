# core/lyapunov_monitor.py

"""
Monitors the stability of the system using Lyapunov analysis.

This module provides the LyapunovMonitor class, which is responsible for
tracking the system's state trajectory and assessing its stability based on
the principles of Lyapunov stability theory.
"""

from __future__ import annotations

import numpy as np
import time
from typing import List, Optional, Tuple, Dict
from scipy import stats

from core.types import SystemState, LyapunovValue, BoundedExcursion, TestResult, ProofObligation
from math_utils import lyapunov, martingales

# Helper functions (mock implementations)

def compute_energy_approx(state: SystemState) -> float:
    """Computes a mock approximation of system energy."""
    return state.approximated_energy

def count_failing_tests(test_results: List[TestResult]) -> int:
    """Counts the number of failing tests."""
    return sum(1 for r in test_results if not r.passed)

def count_open_obligations(proof_obligations: List[ProofObligation]) -> int:
    """Counts the number of open proof obligations."""
    return sum(1 for o in proof_obligations if o.status == 'open')

def classify_excursion_cause(window: List[LyapunovValue], future_window: List[LyapunovValue]) -> str:
    """Classifies the cause of an excursion. Mock implementation."""
    # In a real implementation, this would inspect the state changes that
    # correspond to the Lyapunov value changes in the window.
    return "Test addition"

# Main Lyapunov functions

def compute_lyapunov_function(state: SystemState,
                            kappa: float = 100.0,
                            xi: float = 50.0) -> LyapunovValue:
    """
    Computes the Lyapunov function Φ(S) for a given system state.

    The function is defined as:
    Φ(S) = E_approx(S) + κ·#{failing tests} + ξ·#{open obligations}

    This function acts as a potential function for the system's state space.
    A decrease in this value signifies progress towards a more stable state
    (lower energy, fewer failing tests, fewer open obligations).

    Theorem: Under the assumption of bounded excursions (temporary increases
    in Φ are controlled), the process Φ_t is expected to be a supermartingale,
    which guarantees almost-sure convergence to a stable state.
    """
    energy = compute_energy_approx(state)
    failing_tests = count_failing_tests(state.test_results)
    open_obligations = count_open_obligations(state.proof_obligations)

    test_component = kappa * failing_tests
    obligation_component = xi * open_obligations

    phi = energy + test_component + obligation_component

    return LyapunovValue(
        total=phi,
        energy_component=energy,
        test_component=test_component,
        obligation_component=obligation_component,
        timestamp=time.time()
    )

def detect_bounded_excursions(phi_history: List[LyapunovValue],
                            window_size: int = 50,
                            excursion_tolerance: float = 5.0) -> List[BoundedExcursion]:
    """
    Detects and classifies bounded excursions in the Lyapunov function's trajectory.

    An excursion occurs when Φ increases temporarily, for example, due to the
    addition of new tests (which may initially fail) or new requirements (which
    increase proof obligations). A 'bounded' excursion is one where this increase
    is temporary and followed by a recovery, keeping the system on a stable path.
    """
    excursions = []
    if len(phi_history) < window_size:
        return excursions

    for i in range(window_size, len(phi_history)):
        window = phi_history[i-window_size:i]

        # Compute trend over the window
        phi_values = [v.total for v in window]
        time_indices = range(len(phi_values))
        try:
            trend_slope = np.polyfit(time_indices, phi_values, 1)[0]
        except np.linalg.LinAlgError:
            continue # Skip if fitting fails

        # Detect a potential excursion: an increasing trend in the window
        if trend_slope > 0:
            # Look ahead to see if the trend reverses (recovery)
            future_window_end = min(i + window_size, len(phi_history))
            future_window = phi_history[i:future_window_end]

            if len(future_window) > 1:
                future_values = [v.total for v in future_window]
                future_time_indices = range(len(future_values))
                try:
                    recovery_slope = np.polyfit(future_time_indices, future_values, 1)[0]
                except np.linalg.LinAlgError:
                    continue

                # If recovery is significant enough, classify the excursion
                if recovery_slope < -0.1:  # Threshold for a clear recovery trend
                    max_excursion_val = max(phi_values)
                    # Baseline is taken from the start of the window
                    baseline_val = phi_values[0]
                    magnitude = max_excursion_val - baseline_val

                    if magnitude <= excursion_tolerance:
                        excursions.append(BoundedExcursion(
                            start_index=i - window_size,
                            end_index=i + len(future_window) -1,
                            magnitude=magnitude,
                            # Cause classification is mocked for now
                            cause=classify_excursion_cause(window, future_window)
                        ))

    return excursions

def verify_martingale_convergence(phi_history: List[LyapunovValue],
                                warmup_period: int = 100) -> bool:
    """
    Verifies that the Lyapunov function trajectory (Φ_t) forms a supermartingale
    after an initial warmup period. This is a key part of the proof of
    almost-sure convergence.

    Theorem (Doob's Supermartingale Convergence Theorem):
    If a supermartingale X_t is bounded below (i.e., X_t >= C for some constant C),
    then it converges almost surely to a random variable X.

    In our case, Φ_t is bounded below by 0. We need to verify the supermartingale
    property: E[Φ_{t+1} | F_t] ≤ Φ_t. We test for a stronger condition,
    E[Φ_{t+1} | F_t] ≤ Φ_t - ε, which implies a drift towards lower values.
    """
    if len(phi_history) < warmup_period + 50:
        return False  # Insufficient data for a reliable statistical test

    # Extract post-warmup values for the test
    post_warmup_phi = [v.total for v in phi_history[warmup_period:]]

    # We test the supermartingale property by looking at the differences
    # d_t = Φ_t - Φ_{t+1}. If Φ is a supermartingale, we expect E[d_t | F_t] >= 0.
    # We test for a stronger condition: is the mean of d_t significantly positive?
    decrements = np.diff(post_warmup_phi) * -1 # d_t = phi_t - phi_{t+1}

    if len(decrements) < 30: # Need enough samples for t-test
        return False

    # Perform a one-sided t-test to see if the mean decrement is > 0.
    # H0: mean_decrement <= 0 (not a supermartingale with positive drift)
    # H1: mean_decrement > 0 (is a supermartingale with positive drift)
    mean_decrement = np.mean(decrements)
    std_dev = np.std(decrements, ddof=1)

    if std_dev == 0:
        # If there's no variance, it's not converging unless it's already at minimum.
        # We can say it's not converging in a meaningful way.
        return False

    # Calculate the t-statistic
    t_stat = mean_decrement / (std_dev / np.sqrt(len(decrements)))

    # Calculate the p-value for the one-sided test
    p_value = 1 - stats.t.cdf(t_stat, df=len(decrements)-1)

    # We conclude convergence if the p-value is low enough (e.g., < 0.05)
    # and the mean decrement is practically significant ( > epsilon).
    is_converging = p_value < 0.05 and mean_decrement > 1e-6

    return is_converging


# Constants for stability analysis
DEFAULT_EXCURSION_BOUND = 1.5
DEFAULT_CONVERGENCE_THRESHOLD = 1e-6
MAX_HISTORY_SIZE = 1000

class LyapunovMonitor:
    """
    Monitors system stability by computing Lyapunov potentials and tracking excursions.
    """

    def __init__(self, excursion_bound: float = DEFAULT_EXCURSION_BOUND,
                 convergence_threshold: float = DEFAULT_CONVERGENCE_THRESHOLD):
        """
        Initializes the LyapunovMonitor.
        """
        self.excursion_bound = excursion_bound
        self.convergence_threshold = convergence_threshold
        self.phi_history: List[LyapunovValue] = []

    def track_state(self, state: SystemState):
        """
        Computes the Lyapunov value for the new state and adds it to the history.
        """
        phi = compute_lyapunov_function(state)
        self.phi_history.append(phi)

        if len(self.phi_history) > MAX_HISTORY_SIZE:
            self.phi_history.pop(0)

    def analyze_stability(self) -> Dict[str, any]:
        """
        Performs a full stability analysis on the current history.
        """
        convergence = verify_martingale_convergence(self.phi_history)
        excursions = detect_bounded_excursions(self.phi_history)

        return {
            "martingale_convergence": convergence,
            "bounded_excursions": excursions
        }

    def reset(self):
        """
        Resets the monitor's history.
        """
        self.phi_history.clear()
