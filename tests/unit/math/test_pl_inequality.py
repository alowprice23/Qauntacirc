import pytest
import numpy as np
from math_utils.pl_inequality import (
    verify_pl_inequality,
    pl_convergence_rate,
    global_optimization_guarantee
)

# A simple quadratic function that is strongly convex and thus PL
def quadratic_func(x):
    return np.sum(x**2)

def quadratic_grad(x):
    return 2 * x

# A non-convex function that is known to be PL
# f(x) = (x^2 - a^2)^2, for |x| > a/sqrt(2), it's PL
def non_convex_pl_func(x):
    a = 2
    if np.abs(x) > a / np.sqrt(2):
        return (x**2 - a**2)**2
    return 0 # Not PL in this region

def non_convex_pl_grad(x):
    a = 2
    return 4 * x * (x**2 - a**2)

# A function that is not PL (e.g., f(x) = x^4)
def non_pl_func(x):
    return x[0]**4

def non_pl_grad(x):
    return np.array([4 * x[0]**3])

def test_verify_pl_inequality_quadratic():
    x_optimal = np.array([0.0, 0.0])
    space = (-10, 10, 2)
    # For f(x) = ||x||^2, mu = 2.
    satisfied, mu_estimated = verify_pl_inequality(quadratic_func, quadratic_grad, x_optimal, space)
    assert satisfied
    assert mu_estimated > 0

    # Verify with a known mu
    satisfied_known, _ = verify_pl_inequality(quadratic_func, quadratic_grad, x_optimal, space, mu=1.0)
    assert satisfied_known

def test_verify_pl_inequality_non_pl():
    x_optimal = np.array([0.0])
    space = (-1, 1, 1) # Reduce space to focus on area around 0
    satisfied, mu_estimated = verify_pl_inequality(non_pl_func, non_pl_grad, x_optimal, space, mu=0.1)
    assert not satisfied

def test_pl_convergence_rate():
    mu = 0.1
    step_size = 0.5
    # rate = 1 - 2 * 0.1 * 0.5 = 1 - 0.1 = 0.9
    assert pl_convergence_rate(mu, step_size) == pytest.approx(0.9)

    # Test with invalid inputs
    with pytest.raises(ValueError):
        pl_convergence_rate(0, 0.5)
    with pytest.raises(ValueError):
        pl_convergence_rate(0.1, 0)
    with pytest.raises(ValueError):
        pl_convergence_rate(-0.1, 0.5)

    # Test warning for large step size
    assert pl_convergence_rate(0.1, 10) == 0.0

def test_global_optimization_guarantee():
    mu = 0.1
    L = 10.0
    rate = 1 - mu / L
    expected_string = f"Guaranteed linear convergence to global minimum with rate {rate:.4f} (for step_size=1/L)."
    assert global_optimization_guarantee(mu, L) == expected_string

    assert "No guarantee" in global_optimization_guarantee(0, L)
    assert "No guarantee" in global_optimization_guarantee(mu, 0)
