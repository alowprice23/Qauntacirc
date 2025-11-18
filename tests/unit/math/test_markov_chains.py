import pytest
import numpy as np
from math_utils.markov_chains import (
    DiscreteTimeMarkovChain,
    ContinuousTimeMarkovChain
)

@pytest.fixture
def simple_dtmc():
    # A simple 2-state Markov chain
    P = np.array([[0.9, 0.1], [0.5, 0.5]])
    return DiscreteTimeMarkovChain(P)

@pytest.fixture
def reversible_dtmc():
    P = np.array([[0.8, 0.2], [0.2, 0.8]])
    return DiscreteTimeMarkovChain(P)

@pytest.fixture
def simple_ctmc():
    # A simple 2-state continuous-time Markov chain
    Q = np.array([[-0.1, 0.1], [0.5, -0.5]])
    return ContinuousTimeMarkovChain(Q)

def test_dtmc_init():
    with pytest.raises(ValueError):
        DiscreteTimeMarkovChain(np.array([[0.5, 0.6], [0.5, 0.5]]))

def test_dtmc_stationary_distribution(simple_dtmc):
    pi = simple_dtmc.get_stationary_distribution()
    assert len(pi) == 2
    assert np.isclose(np.sum(pi), 1.0)
    # Check pi * P = pi
    assert np.allclose(pi @ simple_dtmc.P, pi)

def test_dtmc_is_reversible(reversible_dtmc):
    pi = reversible_dtmc.get_stationary_distribution()
    assert reversible_dtmc.is_reversible(pi)

    # A non-reversible 3-state cycle
    non_rev_P = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    non_rev_mc = DiscreteTimeMarkovChain(non_rev_P)
    pi_non_rev = non_rev_mc.get_stationary_distribution()
    assert not non_rev_mc.is_reversible(pi_non_rev)

def test_dtmc_mixing_time_bound(reversible_dtmc):
    bound = reversible_dtmc.mixing_time_bound()
    assert bound > 0

def test_ctmc_init():
    with pytest.raises(ValueError):
        ContinuousTimeMarkovChain(np.array([[-0.1, 0.2], [0.5, -0.5]]))

def test_ctmc_transition_matrix_at_t(simple_ctmc):
    t = 1.0
    P_t = simple_ctmc.get_transition_matrix_at_t(t)
    assert P_t.shape == (2, 2)
    # Rows should sum to 1
    assert np.allclose(np.sum(P_t, axis=1), 1.0)

def test_ctmc_stationary_distribution(simple_ctmc):
    pi = simple_ctmc.get_stationary_distribution()
    assert len(pi) == 2
    assert np.isclose(np.sum(pi), 1.0)
    # Check pi * Q = 0
    assert np.allclose(pi @ simple_ctmc.Q, np.zeros(2), atol=1e-9)
