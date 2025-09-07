import numpy as np

def is_contraction_mapping(func, space, k=None, samples=1000):
    """
    Verifies if a function is a contraction mapping on a given space.

    A function f is a contraction mapping if there exists a k in [0, 1) such that
    ||f(x) - f(y)|| <= k * ||x - y|| for all x, y in the space.

    Args:
        func (callable): The function to check.
        space (tuple): A tuple defining the space, e.g., (lower_bound, upper_bound, dim).
        k (float, optional): The contraction factor. If None, it will be estimated.
        samples (int): The number of sample pairs to test.

    Returns:
        bool: True if the function is a contraction mapping, False otherwise.
        float: The estimated or verified contraction factor.
    """
    lower_bound, upper_bound, dim = space
    max_k = 0

    for _ in range(samples):
        x = np.random.uniform(lower_bound, upper_bound, dim)
        y = np.random.uniform(lower_bound, upper_bound, dim)

        if np.all(x == y):
            continue

        dist_xy = np.linalg.norm(x - y)
        dist_fxfy = np.linalg.norm(func(x) - func(y))

        current_k = dist_fxfy / dist_xy
        if current_k > max_k:
            max_k = current_k

    if k is not None:
        return max_k <= k, max_k
    else:
        return max_k < 1.0, max_k

def banach_fixed_point(func, x0, max_iter=1000, tol=1e-6):
    """
    Finds the fixed point of a contraction mapping using the Banach fixed-point theorem.

    Args:
        func (callable): The contraction mapping.
        x0 (np.ndarray): The initial guess.
        max_iter (int): The maximum number of iterations.
        tol (float): The tolerance for convergence.

    Returns:
        np.ndarray: The fixed point of the function.
        int: The number of iterations performed.
    """
    x = x0
    for i in range(max_iter):
        x_next = func(x)
        if np.linalg.norm(x_next - x) < tol:
            return x_next, i + 1
        x = x_next

    raise RuntimeError("Fixed point iteration did not converge.")

def estimate_convergence_rate(k):
    """
    Estimates the convergence rate for an iterative method based on its contraction factor.

    The error at iteration n, e_n, is bounded by e_n <= k^n * e_0.

    Args:
        k (float): The contraction factor (must be in [0, 1)).

    Returns:
        float: The convergence rate (the base of the exponential decay).
    """
    if not (0 <= k < 1):
        raise ValueError("Contraction factor k must be in the interval [0, 1).")
    return k

def verify_lipschitz_constant(func, space, L, samples=1000):
    """
    Verifies if L is a valid Lipschitz constant for the function on the given space.

    Args:
        func (callable): The function to check.
        space (tuple): A tuple defining the space, e.g., (lower_bound, upper_bound, dim).
        L (float): The proposed Lipschitz constant.
        samples (int): The number of sample pairs to test.

    Returns:
        bool: True if L is a valid Lipschitz constant, False otherwise.
    """
    is_contraction, estimated_k = is_contraction_mapping(func, space, k=L, samples=samples)
    return estimated_k <= L
