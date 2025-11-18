import numpy as np
from .line_search import armijo_backtracking

def hessian_vector_product(grad, x, v, epsilon=1e-4):
    """
    Computes the Hessian-vector product H*v using finite differences.
    This method avoids explicit construction of the Hessian matrix.

    The Hessian-vector product is approximated by the finite difference:
    H*v approx= (grad(f(x + epsilon * v)) - grad(f(x))) / epsilon

    Args:
        grad (callable): The gradient of the function f.
        x (np.ndarray): The point at which to evaluate the Hessian-vector product.
        v (np.ndarray): The vector to multiply the Hessian by.
        epsilon (float): A small step size for the finite difference.

    Returns:
        np.ndarray: The product of the Hessian and the vector v.
    """
    grad_x = grad(x)
    grad_x_plus_eps_v = grad(x + epsilon * v)
    return (grad_x_plus_eps_v - grad_x) / epsilon


def conjugate_gradient_hessian_free(A, b, x0=None, max_iter=100, tol=1e-5):
    """
    Solves the linear system Ax = b using the conjugate gradient method,
    where A is provided as a function that computes the matrix-vector product.

    Args:
        A (callable): A function that computes A*v (the Hessian-vector product).
        b (np.ndarray): The vector b in the equation Ax = b.
        x0 (np.ndarray, optional): The initial guess for x. Defaults to a zero vector.
        max_iter (int): The maximum number of iterations.
        tol (float): The tolerance for convergence.

    Returns:
        np.ndarray: The solution vector x.
    """
    if x0 is None:
        x = np.zeros_like(b)
    else:
        x = x0

    r = b - A(x)
    p = r
    rs_old = np.dot(r, r)

    for i in range(max_iter):
        Ap = A(p)
        alpha = rs_old / np.dot(p, Ap)
        x = x + alpha * p
        r = r - alpha * Ap
        rs_new = np.dot(r, r)

        if np.sqrt(rs_new) < tol:
            break

        p = r + (rs_new / rs_old) * p
        rs_old = rs_new

    return x


def hessian_free_optimization(f, grad, x0, max_iter=100, tol=1e-5):
    """
    Performs Hessian-free optimization (Newton-CG method).

    Args:
        f (callable): The objective function to minimize.
        grad (callable): The gradient of the objective function.
        x0 (np.ndarray): The initial guess.
        max_iter (int): Maximum number of outer loop iterations.
        tol (float): Tolerance for gradient norm to determine convergence.

    Returns:
        np.ndarray: The optimal parameters found.
    """
    x = x0
    for i in range(max_iter):
        gradient = grad(x)
        if np.linalg.norm(gradient) < tol:
            print(f"Convergence reached at iteration {i}.")
            break

        # Define the Hessian-vector product function for the current point x
        def H_v(v):
            return hessian_vector_product(grad, x, v)

        # Solve the Newton system H*p = -g using Conjugate Gradient
        # This gives the search direction p.
        p = conjugate_gradient_hessian_free(H_v, -gradient)

        # Use a line search to find a suitable step size alpha
        alpha = armijo_backtracking(f, grad, x, p)

        x = x + alpha * p

    return x
