import numpy as np

def armijo_backtracking(f, grad_f, x, p, alpha=1.0, c1=1e-4, beta=0.5):
    """
    Performs Armijo backtracking line search to find a suitable step size.

    This method ensures that the step size alpha satisfies the Armijo condition:
    f(x + alpha * p) <= f(x) + c1 * alpha * grad(f(x)).T * p

    Args:
        f (callable): The objective function.
        grad_f (callable): The gradient of the objective function.
        x (np.ndarray): The current point.
        p (np.ndarray): The search direction.
        alpha (float): The initial step size.
        c1 (float): The constant for the Armijo condition.
        beta (float): The backtracking factor (0 < beta < 1).

    Returns:
        float: A step size alpha that satisfies the Armijo condition.
    """
    fx = f(x)
    grad_fx_p = np.dot(grad_f(x), p)

    while f(x + alpha * p) > fx + c1 * alpha * grad_fx_p:
        alpha *= beta

    return alpha

def wolfe_line_search(f, grad_f, x, p, alpha_init=1.0, c1=1e-4, c2=0.9, max_iter=20):
    """
    Finds a step size that satisfies the strong Wolfe conditions.
    This is a more robust implementation using a bracketing and zoom strategy.
    """
    alpha = alpha_init
    alpha_prev = 0
    f_x = f(x)
    grad_x_p = np.dot(grad_f(x), p)

    for i in range(max_iter):
        x_new = x + alpha * p
        f_alpha = f(x_new)

        # Check Armijo condition
        if (f_alpha > f_x + c1 * alpha * grad_x_p) or (i > 0 and f_alpha >= f(x + alpha_prev * p)):
            return _zoom(f, grad_f, x, p, alpha_prev, alpha, f_x, grad_x_p, c1, c2)

        grad_alpha = grad_f(x_new)
        grad_alpha_p = np.dot(grad_alpha, p)

        # Check strong Wolfe curvature condition
        if abs(grad_alpha_p) <= abs(c2 * grad_x_p):
            return alpha

        if grad_alpha_p >= 0:
            return _zoom(f, grad_f, x, p, alpha, alpha_prev, f_x, grad_x_p, c1, c2)

        alpha_prev = alpha
        alpha *= 2 # Increase step size

    return alpha # Return best guess if max_iter is reached

def _zoom(f, grad_f, x, p, alpha_lo, alpha_hi, f_x, grad_x_p, c1, c2, max_iter=20):
    """
    Auxiliary function for wolfe_line_search. Narrows down a bracket
    [alpha_lo, alpha_hi] to find a step size satisfying Wolfe conditions.
    """
    f_lo = f(x + alpha_lo * p)

    for i in range(max_iter):
        # Use bisection or interpolation to find a new alpha
        alpha = (alpha_lo + alpha_hi) / 2

        x_new = x + alpha * p
        f_alpha = f(x_new)

        if (f_alpha > f_x + c1 * alpha * grad_x_p) or (f_alpha >= f_lo):
            alpha_hi = alpha
        else:
            grad_alpha = grad_f(x_new)
            grad_alpha_p = np.dot(grad_alpha, p)

            if abs(grad_alpha_p) <= abs(c2 * grad_x_p):
                return alpha

            if grad_alpha_p * (alpha_hi - alpha_lo) >= 0:
                alpha_hi = alpha_lo

            alpha_lo = alpha
            f_lo = f_alpha # Update f_lo for the next iteration

    return alpha # Return best guess if max_iter is reached
