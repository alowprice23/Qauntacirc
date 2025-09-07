import numpy as np

def verify_pl_inequality(func, grad_func, x_optimal, space, mu=None, samples=1000):
    """
    Verifies if a function satisfies the Polyak-Łojasiewicz (PL) inequality.

    The PL inequality states that for a function f, there exists mu > 0 such that
    0.5 * ||grad(f(x))||^2 >= mu * (f(x) - f(x*)) for all x. This is a sufficient
    condition for global linear convergence of gradient descent, even for non-convex
    functions.

    Args:
        func (callable): The function f(x).
        grad_func (callable): The gradient of the function, grad(f(x)).
        x_optimal (np.ndarray): The optimal point x* where f(x*) is the minimum value.
        space (tuple): A tuple defining the space, e.g., (lower_bound, upper_bound, dim).
        mu (float, optional): The PL constant to verify. If None, it will be estimated.
        samples (int): The number of sample points to test.

    Returns:
        bool: True if the function satisfies the PL inequality, False otherwise.
        float: The estimated or verified PL constant mu.
    """
    lower_bound, upper_bound, dim = space
    f_optimal = func(x_optimal)
    min_mu = np.inf

    for _ in range(samples):
        x = np.random.uniform(lower_bound, upper_bound, dim)
        f_x = func(x)
        grad_x_norm_sq = np.linalg.norm(grad_func(x))**2

        func_diff = f_x - f_optimal
        if func_diff > 1e-9: # Avoid division by zero or small numbers
            current_mu = (0.5 * grad_x_norm_sq) / func_diff
            if current_mu < min_mu:
                min_mu = current_mu

    if min_mu == np.inf:
        return False, 0 # Could not find a valid mu

    if mu is not None:
        return min_mu >= mu, min_mu
    else:
        # A small tolerance to account for numerical precision
        return min_mu > 1e-9, min_mu

def pl_convergence_rate(mu, step_size):
    """
    Calculates the linear convergence rate for gradient descent under the PL inequality.

    The error e_k = f(x_k) - f(x*) decreases as e_k <= (1 - 2*mu*step_size)^k * e_0.
    The returned value is the base of the exponential convergence.

    Args:
        mu (float): The PL constant.
        step_size (float): The learning rate used in gradient descent.

    Returns:
        float: The convergence rate factor. A smaller value means faster convergence.
    """
    if mu <= 0:
        raise ValueError("PL constant mu must be positive.")
    if step_size <= 0:
        raise ValueError("Step size must be positive.")

    rate = 1 - 2 * mu * step_size

    if rate <= 0:
        print("Warning: The step size may be too large, leading to divergence.")
        return 0.0

    return rate

def global_optimization_guarantee(mu, L):
    """
    Provides a guarantee for global optimization based on PL and smoothness constants.

    If a function is L-smooth and mu-PL, then gradient descent with step size 1/L
    converges linearly to the global minimum.

    Args:
        mu (float): The PL constant.
        L (float): The smoothness (Lipschitz) constant of the gradient.

    Returns:
        str: A string describing the optimization guarantee.
    """
    if mu > 0 and L > 0:
        rate = 1 - mu / L
        return f"Guaranteed linear convergence to global minimum with rate {rate:.4f} (for step_size=1/L)."
    else:
        return "No guarantee of global convergence from these parameters."
