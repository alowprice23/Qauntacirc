import pytest
import numpy as np
from math_utils.info_entropy import (
    shannon_entropy,
    mutual_information,
    kl_divergence,
    cross_entropy
)

def test_shannon_entropy():
    # Uniform distribution (4 outcomes) -> H = log2(4) = 2
    uniform_dist = np.array([0.25, 0.25, 0.25, 0.25])
    assert shannon_entropy(uniform_dist) == pytest.approx(2.0)

    # Certain outcome -> H = 0
    certain_dist = np.array([1.0, 0.0, 0.0, 0.0])
    assert shannon_entropy(certain_dist) == pytest.approx(0.0)

    # A known distribution
    dist = np.array([0.5, 0.5])
    assert shannon_entropy(dist) == pytest.approx(1.0)

def test_mutual_information():
    # Independent variables: P(X,Y) = P(X)P(Y) -> I(X;Y) = 0
    p_x = np.array([0.5, 0.5])
    p_y = np.array([0.25, 0.75])
    joint_dist_ind = np.outer(p_x, p_y)
    assert mutual_information(joint_dist_ind) == pytest.approx(0.0, abs=1e-9)

    # Dependent variables
    # P(X,Y) = [[0.5, 0], [0, 0.5]] -> H(X)=1, H(Y)=1, H(X,Y)=1 -> I(X;Y)=1
    joint_dist_dep = np.array([[0.5, 0], [0, 0.5]])
    assert mutual_information(joint_dist_dep) == pytest.approx(1.0)

def test_kl_divergence():
    p = np.array([0.5, 0.5])
    q = np.array([0.5, 0.5])
    # D_KL(P || P) = 0
    assert kl_divergence(p, q) == pytest.approx(0.0)

    p = np.array([0.9, 0.1])
    q = np.array([0.1, 0.9])
    # A known value
    expected = 0.9 * np.log2(0.9/0.1) + 0.1 * np.log2(0.1/0.9)
    assert kl_divergence(p, q) == pytest.approx(expected)

def test_cross_entropy():
    p = np.array([0.5, 0.5])
    q = np.array([0.5, 0.5])
    # H(P, P) = H(P)
    assert cross_entropy(p, q) == pytest.approx(shannon_entropy(p))

    p = np.array([0.9, 0.1])
    q = np.array([0.1, 0.9])
    # A known value
    expected = -(0.9 * np.log2(0.1) + 0.1 * np.log2(0.9))
    assert cross_entropy(p, q) == pytest.approx(expected)
