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
    which guarantees almost-sure convergence to a stable state. See proofs/lyapunov_convergence.md
    for a detailed proof.
    """
    energy = compute_energy_approx(state)
    failing_tests = count_failing_tests(state.test_results)
    open_obligations = count_open_obligations(state.proof_obligations)

    phi = energy + kappa * failing_tests + xi * open_obligations

    return LyapunovValue(
        total=phi,
        energy_component=energy,
        test_component=kappa * failing_tests,
        obligation_component=xi * open_obligations,
        timestamp=time.time()
    )

def detect_bounded_excursions(phi_history: List[LyapunovValue],
                            window_size: int = 50,
                            excursion_tolerance: float = 5.0) -> List[BoundedExcursion]:
    """
    Detect and classify bounded excursions in Φ trajectory

    Excursion occurs when Φ increases temporarily due to:
    - Adding new tests (increases failing count initially)
    - Adding new requirements (increases obligations)
    """
    excursions = []

    for i in range(window_size, len(phi_history)):
        window = phi_history[i-window_size:i]

        # Compute trend over window
        phi_values = [v.total for v in window]
        trend_slope = np.polyfit(range(len(phi_values)), phi_values, 1)[0]

        # Detect excursion: temporary increase followed by decrease
        if trend_slope > 0:  # Increasing trend
            # Look ahead for recovery
            future_window = phi_history[i:min(i+window_size, len(phi_history))]
            if future_window:
                future_values = [v.total for v in future_window]
                recovery_slope = np.polyfit(range(len(future_values)), future_values, 1)[0]

                if recovery_slope < -0.1:  # Recovering (decreasing)
                    max_excursion = max(phi_values) - min(phi_values[:window_size//2])
                    if max_excursion <= excursion_tolerance:
                        excursions.append(BoundedExcursion(
                            start_index=i-window_size,
                            end_index=i+len(future_window),
                            magnitude=max_excursion,
                            cause=classify_excursion_cause(window, future_window)
                        ))

    return excursions

def verify_martingale_convergence(phi_history: List[LyapunovValue],
                                warmup_period: int = 100) -> bool:
    """
    Verify that Φ_t forms a supermartingale after warmup period

    Theorem: If E[Φ_{t+1} | Φ_t] ≤ Φ_t - ε_min for t ≥ T_0,
    then Φ_t converges almost surely
    """
    if len(phi_history) < warmup_period + 50:
        return False  # Insufficient data

    # Extract post-warmup values
    post_warmup = phi_history[warmup_period:]
    phi_values = [v.total for v in post_warmup]

    # Compute conditional expectations (approximated via windowed averages)
    conditional_decrements = []
    window_size = 10

    for i in range(window_size, len(phi_values) - 1):
        current_phi = phi_values[i]
        next_phi = phi_values[i + 1]

        # Estimate E[Φ_{t+1} | Φ_t] via local averaging
        local_context = phi_values[i-window_size:i]
        expected_next = np.mean([phi_values[j+1] for j in range(i-window_size, i)])

        decrement = current_phi - expected_next
        conditional_decrements.append(decrement)

    # Test supermartingale property: decrements should be positive on average
    mean_decrement = np.mean(conditional_decrements)

    # Statistical test: is mean significantly > 0?
    t_stat = mean_decrement / (np.std(conditional_decrements) / np.sqrt(len(conditional_decrements)))
    p_value = 1 - stats.norm.cdf(t_stat)

    return p_value < 0.05 and mean_decrement > 1e-6  # Significant positive drift


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
