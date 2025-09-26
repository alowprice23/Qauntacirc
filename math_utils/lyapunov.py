"""
Lyapunov stability functions for discrete state-space optimization.
"""
from typing import List
import numpy as np

def calculate_lyapunov_potential(
    energy: float,
    num_failing_tests: int,
    num_open_obligations: int,
    kappa: float,
    xi: float
) -> float:
    """
    Calculates the Lyapunov potential as defined in the README.md.
    Φ(S) = E(S) + κ·#{failing tests} + ξ·#{open obligations}

    Args:
        energy (float): The current energy of the system, E(S).
        num_failing_tests (int): The number of failing tests.
        num_open_obligations (int): The number of open obligations.
        kappa (float): The weight for failing tests.
        xi (float): The weight for open obligations.

    Returns:
        float: The calculated Lyapunov potential Φ(S).
    """
    return energy + (kappa * num_failing_tests) + (xi * num_open_obligations)

def check_bounded_excursion(
    potential_history: List[float],
    max_increase_fraction: float = 0.1,
    window_size: int = 10
) -> bool:
    """
    Checks if the Lyapunov potential is experiencing a bounded excursion.
    An excursion is a temporary increase in the potential.

    Args:
        potential_history (List[float]): A history of Lyapunov potential values.
        max_increase_fraction (float): The maximum allowed fractional increase
                                     relative to the minimum potential in the window.
        window_size (int): The size of the sliding window to analyze.

    Returns:
        bool: True if the potential is stable or in a bounded excursion,
              False if it appears to be diverging.
    """
    if len(potential_history) < window_size:
        return True  # Not enough data to determine divergence

    window = potential_history[-window_size:]
    min_in_window = np.min(window)
    max_in_window = np.max(window)

    if min_in_window == 0: # Avoid division by zero
        return max_in_window <= 0

    increase = max_in_window - min_in_window
    if increase <= 0:
        return True # Not an excursion, it's stable or decreasing

    allowed_increase = abs(min_in_window) * max_increase_fraction
    return increase <= allowed_increase

def estimate_lyapunov_exponent(time_series: np.ndarray) -> float:
    """
    Estimates the Lyapunov exponent for a time series.
    A negative exponent suggests convergence.
    """
    if len(time_series) < 2:
        return 0.0

    # Calculate the logarithm of the ratio of successive terms
    # To avoid issues with zero or negative values, we analyze the separation
    diffs = np.abs(np.diff(time_series))

    # Filter out zero differences to avoid log(0)
    non_zero_diffs = diffs[diffs > 0]
    if len(non_zero_diffs) < 2:
        return 0.0

    log_ratios = np.log(non_zero_diffs[1:] / non_zero_diffs[:-1])

    return np.mean(log_ratios)
