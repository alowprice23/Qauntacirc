import pytest
import numpy as np
from math_utils.lipschitz import (
    estimate_lipschitz_constant,
    verify_lipschitz_continuity,
    gradient_bound_from_lipschitz,
    lipschitz_convergence_implications
)

# A linear function f(x) = 2x, with Lipschitz constant 2
def linear_func(x):
    return 2 * x

# A function with a known Lipschitz constant, f(x) = sin(x), L=1
def sin_func(x):
    return np.sin(x)

def test_estimate_lipschitz_constant():
    space = (-10, 10, 1)
    # For f(x) = 2x, L = 2
    L_estimated = estimate_lipschitz_constant(linear_func, space)
    assert L_estimated == pytest.approx(2.0)

    # For f(x) = sin(x), L = 1
    space_sin = (-np.pi, np.pi, 1)
    L_sin_estimated = estimate_lipschitz_constant(sin_func, space_sin)
    assert L_sin_estimated == pytest.approx(1.0, abs=1e-2)

def test_verify_lipschitz_continuity():
    space = (-10, 10, 1)
    # For f(x) = 2x, L=2 is a valid constant
    assert verify_lipschitz_continuity(linear_func, space, L=2.0)
    assert verify_lipschitz_continuity(linear_func, space, L=2.1)
    assert not verify_lipschitz_continuity(linear_func, space, L=1.9)

def test_gradient_bound_from_lipschitz():
    L = 10.0
    space = (-1, 1, 1)
    expected_string = f"Gradient norm variation is bounded by L={L:.4f} across the space."
    assert gradient_bound_from_lipschitz(L, space) == expected_string

def test_lipschitz_convergence_implications():
    L = 10.0
    # Suitable learning rate: lr < 2/L = 0.2
    lr_suitable = 0.1
    assert "suitable" in lipschitz_convergence_implications(L, lr_suitable)

    # Unsuitable learning rate: lr >= 2/L = 0.2
    lr_unsuitable = 0.2
    assert "Warning" in lipschitz_convergence_implications(L, lr_unsuitable)
    lr_too_large = 0.3
    assert "Warning" in lipschitz_convergence_implications(L, lr_too_large)
