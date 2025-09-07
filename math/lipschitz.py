import numpy as np

def estimate_lipschitz_constant(func, space, samples=1000):
    """
    Estimates the Lipschitz constant L of a function over a given space.

    A function f is L-Lipschitz continuous if ||f(x) - f(y)|| <= L * ||x - y|| for all x, y.

    Args:
        func (callable): The function to analyze.
        space (tuple): A tuple defining the space, e.g., (lower_bound, upper_bound, dim).
        samples (int): The number of sample pairs to test.

    Returns:
        float: The estimated Lipschitz constant.
    """
    lower_bound, upper_bound, dim = space
    max_l = 0.0

    for _ in range(samples):
        x = np.random.uniform(lower_bound, upper_bound, dim)
        y = np.random.uniform(lower_bound, upper_bound, dim)

        dist_xy = np.linalg.norm(x - y)
        if dist_xy < 1e-9:
            continue

        dist_fxfy = np.linalg.norm(func(x) - func(y))

        current_l = dist_fxfy / dist_xy
        if current_l > max_l:
            max_l = current_l

    return max_l

def verify_lipschitz_continuity(func, space, L, samples=1000):
    """
    Verifies if a function is L-Lipschitz continuous.

    Args:
        func (callable): The function to analyze.
        space (tuple): A tuple defining the space.
        L (float): The proposed Lipschitz constant.
        samples (int): The number of sample pairs to test.

    Returns:
        bool: True if the function is L-Lipschitz continuous, False otherwise.
    """
    estimated_L = estimate_lipschitz_constant(func, space, samples)
    return estimated_L <= L

def gradient_bound_from_lipschitz(L, space):
    """
    Computes an upper bound on the gradient norm if the function is convex and L-smooth.

    If f is convex and L-smooth, then ||grad(f(x))||^2 <= 2L(f(x) - f(x*)).
    This function can't be fully implemented without knowing f(x*), so it's illustrative.
    """
    lower_bound, upper_bound, _ = space
    domain_diameter = np.linalg.norm(upper_bound - lower_bound)
    # A different bound: ||grad(f(x)) - grad(f(y))|| <= L ||x-y||
    # This implies that the gradient cannot change arbitrarily fast.
    return f"Gradient norm variation is bounded by L={L:.4f} across the space."


def lipschitz_convergence_implications(L, learning_rate):
    """
    Describes the implications of the Lipschitz constant on gradient descent convergence.

    For gradient descent to converge, the learning rate must be less than 2/L.
    """
    if learning_rate >= 2 / L:
        return f"Warning: Learning rate {learning_rate:.4f} may be too large. For convergence, it should be < {2/L:.4f}."
    else:
        return f"Learning rate {learning_rate:.4f} is suitable for convergence with L={L:.4f}."
