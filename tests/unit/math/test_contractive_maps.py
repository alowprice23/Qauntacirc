import pytest
import numpy as np
from math_utils.contractive_maps import (
    is_contraction_mapping,
    banach_fixed_point,
    estimate_convergence_rate,
    verify_lipschitz_constant
)

# A simple contraction mapping: f(x) = x / 2
def contraction_func(x):
    return x / 2.0

# A function that is not a contraction mapping: f(x) = 2x
def non_contraction_func(x):
    return x * 2.0

# A Lipschitz continuous function: f(x) = sin(x)
def lipschitz_func(x):
    return np.sin(x)

def test_is_contraction_mapping_true():
    space = (-10, 10, 1)
    is_contraction, k_estimated = is_contraction_mapping(contraction_func, space)
    assert is_contraction
    assert k_estimated == pytest.approx(0.5)

    # Verify with a known k
    is_contraction_known, _ = is_contraction_mapping(contraction_func, space, k=0.6)
    assert is_contraction_known

def test_is_contraction_mapping_false():
    space = (-10, 10, 1)
    is_contraction, k_estimated = is_contraction_mapping(non_contraction_func, space)
    assert not is_contraction
    assert k_estimated == pytest.approx(2.0)

def test_banach_fixed_point():
    # The fixed point of f(x) = x/2 is 0
    x0 = np.array([10.0])
    fixed_point, iters = banach_fixed_point(contraction_func, x0)
    assert np.allclose(fixed_point, [0.0], atol=1e-6)
    assert iters > 0

    # Test for non-convergence
    with pytest.raises(RuntimeError):
        banach_fixed_point(non_contraction_func, x0, max_iter=100)

def test_estimate_convergence_rate():
    assert estimate_convergence_rate(0.5) == 0.5
    with pytest.raises(ValueError):
        estimate_convergence_rate(1.0)
    with pytest.raises(ValueError):
        estimate_convergence_rate(-0.1)

def test_verify_lipschitz_constant():
    space = (-np.pi, np.pi, 1)
    # For f(x) = sin(x), the Lipschitz constant is 1
    assert verify_lipschitz_constant(lipschitz_func, space, L=1.0)
    assert not verify_lipschitz_constant(lipschitz_func, space, L=0.9)
    assert verify_lipschitz_constant(non_contraction_func, space, L=2.0)
    assert not verify_lipschitz_constant(non_contraction_func, space, L=1.9)
