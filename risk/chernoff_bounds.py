import math

def chernoff_bound_verified_failure(n: int, epsilon: float) -> float:
    """
    Calculates the Chernoff bound for the probability of verified failure.
    P(verified failure) <= 2 * exp(-2 * n * epsilon^2)

    Args:
        n: Number of verification runs.
        epsilon: Error tolerance.

    Returns:
        The upper bound on the probability of verified failure.
    """
    if n <= 0 or epsilon <= 0:
        raise ValueError("Number of runs (n) and epsilon must be positive.")
    return 2 * math.exp(-2 * n * (epsilon**2))

def chernoff_bound_empirical_failure(m: int, delta: float) -> float:
    """
    Calculates the Chernoff bound for the probability of empirical failure.
    P(empirical failure) <= 2 * exp(-2 * m * delta^2)

    Args:
        m: Number of empirical tests.
        delta: Error tolerance for empirical tests.

    Returns:
        The upper bound on the probability of empirical failure.
    """
    if m <= 0 or delta <= 0:
        raise ValueError("Number of tests (m) and delta must be positive.")
    return 2 * math.exp(-2 * m * (delta**2))
