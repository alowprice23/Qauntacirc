import pytest
import numpy as np
from math_utils.verification_utils import (
    ConvergenceCertificate,
    verify_convexity,
    verify_smoothness
)

def test_convergence_certificate():
    cert = ConvergenceCertificate("TestAlgo", {'lr': 0.01})
    assert cert.algorithm_name == "TestAlgo"
    assert cert.params['lr'] == 0.01

    cert.add_log(1, np.array([1, 1]), 0.5, grad_norm=0.1)
    cert.add_log(100, np.array([0, 0]), 0.0, grad_norm=1e-6)

    assert len(cert.log) == 2
    assert cert.log[0]['iteration'] == 1
    assert cert.log[1]['value'] == 0.0

    properties = {
        'is_convex': True,
        'pl_constant': 0.1,
        'is_contraction': True,
        'contraction_factor': 0.9
    }
    proof = cert.generate_proof(properties)

    assert "Certificate for TestAlgo" in proof
    assert "function has been verified as convex" in proof
    assert "PL inequality with mu=0.1000" in proof
    assert "map is a contraction with k=0.9000" in proof
    assert "Final gradient norm 1.00e-06" in proof

def test_verify_convexity():
    # A convex function: f(x) = x^2
    def convex_func(x):
        return np.sum(x**2)

    space = (-10, 10, 2)
    is_convex, msg = verify_convexity(convex_func, space)
    assert is_convex

    # A non-convex function: f(x) = -x^2
    def non_convex_func(x):
        return -np.sum(x**2)

    is_convex, msg = verify_convexity(non_convex_func, space)
    assert not is_convex

def test_verify_smoothness():
    # For f(x) = x^2, grad(f(x)) = 2x.
    # ||2x - 2y|| = 2||x-y||, so L=2.
    def grad_func(x):
        return 2 * x

    space = (-10, 10, 2)
    L_estimated, msg = verify_smoothness(grad_func, space)
    assert L_estimated == pytest.approx(2.0, abs=1e-9)
