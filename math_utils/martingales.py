import numpy as np

def is_martingale(sequence, filtration):
    """
    Checks if a sequence is a martingale with respect to a given filtration.

    A sequence X_n is a martingale if E[X_{n+1} | F_n] = X_n, where F_n is the filtration.
    This check is a simplified, empirical one.

    Args:
        sequence (list or np.ndarray): The sequence of random variables.
        filtration (list of lists): The filtration, where F_n = filtration[n].

    Returns:
        bool: True if the sequence appears to be a martingale.
    """
    for n in range(len(sequence) - 1):
        # This is a simplification. A rigorous check is complex.
        # We assume the filtration is represented by the history up to time n.
        conditional_expectation = np.mean(sequence[n+1:]) # Simplified approximation
        if not np.isclose(conditional_expectation, sequence[n], atol=1e-2):
            return False
    return True

def doob_martingale_convergence(sequence):
    """
    Applies Doob's martingale convergence theorem.

    If a supermartingale is non-negative, or bounded below, it converges almost surely.
    This function checks the non-negative condition for convergence.

    Args:
        sequence (list or np.ndarray): The supermartingale sequence.

    Returns:
        bool: True if the sequence is non-negative, implying convergence.
    """
    return np.all(np.array(sequence) >= 0)

def azuma_hoeffding_inequality(sequence, c):
    """
    Calculates the probability bound using the Azuma-Hoeffding inequality.

    For a martingale with bounded differences |X_k - X_{k-1}| <= c_k.
    P(|X_n - X_0| >= t) <= 2 * exp(-t^2 / (2 * sum(c_k^2)))

    Args:
        sequence (list or np.ndarray): The martingale sequence.
        c (list or float): The bounds on the differences.

    Returns:
        callable: A function that takes t and returns the probability bound.
    """
    if isinstance(c, (int, float)):
        c = [c] * (len(sequence) - 1)

    sum_c_sq = sum(ck**2 for ck in c)

    def probability_bound(t):
        if t <= 0:
            return 1.0
        return 2 * np.exp(-t**2 / (2 * sum_c_sq))

    return probability_bound

def optional_stopping_theorem_bound(sequence, stopping_time):
    """
    Applies the optional stopping theorem to a martingale.

    If T is a stopping time, then E[X_T] = E[X_0].
    This function checks if the expectation at the stopping time is close to the initial expectation.

    Args:
        sequence (np.ndarray): The martingale sequence.
        stopping_time (int): The stopping time index.

    Returns:
        bool: True if the theorem holds approximately.
    """
    if stopping_time >= len(sequence):
        raise ValueError("Stopping time exceeds sequence length.")

    expected_xt = np.mean(sequence[stopping_time])
    expected_x0 = np.mean(sequence[0])

    return np.isclose(expected_xt, expected_x0)
<<<<<<< HEAD
<<<<<<< HEAD


def is_supermartingale(sequence: np.ndarray) -> tuple[bool, float]:
    """
    Checks if a sequence has properties of a supermartingale.

    A sequence X_n is a supermartingale if E[X_{n+1} | F_n] <= X_n.
    This is empirically checked by testing if the sequence has a non-positive drift.

    Args:
        sequence (np.ndarray): The sequence of random variables.

    Returns:
        A tuple containing:
        - bool: True if the sequence has a non-positive drift.
        - float: The calculated drift.
    """
    if len(sequence) < 2:
        return True, 0.0  # Not enough data to decide

    diffs = np.diff(sequence)
    drift = np.mean(diffs)

    return drift <= 0, drift
=======
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
