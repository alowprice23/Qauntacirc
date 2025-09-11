import pytest
import numpy as np
from math_utils.martingales import (
    is_martingale,
    doob_martingale_convergence,
    azuma_hoeffding_inequality,
    optional_stopping_theorem_bound,
    is_supermartingale
)

def test_is_martingale():
    # A simple random walk (martingale)
    np.random.seed(42)
    steps = np.random.choice([-1, 1], size=100)
    random_walk = np.cumsum(steps)
    # The simplified check in the function might not pass for a true martingale
    assert is_martingale(random_walk, None)

def test_doob_martingale_convergence():
    assert doob_martingale_convergence([1, 0.5, 0.25])
    assert not doob_martingale_convergence([1, -0.5, 0.25])

def test_azuma_hoeffding_inequality():
    sequence = [0, 1, 0, 1, 2]
    c = 1
    prob_bound_func = azuma_hoeffding_inequality(sequence, c)

    t = 2.0
    sum_c_sq = 4 * c**2
    expected_bound = 2 * np.exp(-t**2 / (2 * sum_c_sq))

    assert prob_bound_func(t) == pytest.approx(expected_bound)
    assert prob_bound_func(0) == 1.0

def test_optional_stopping_theorem_bound():
    # For a simple random walk, E[X_T] = E[X_0] = 0
    sequence = np.array([0, 1, 2, 1, 0, -1, 0])
    # The function expects a single value for sequence[stopping_time], not an array
    # This test will fail if the implementation is not for a single path
    # The current implementation np.mean(sequence[stopping_time]) is for a single path
    assert optional_stopping_theorem_bound(sequence, stopping_time=4)

def test_is_supermartingale():
    # Sequence with negative drift
    supermartingale = np.array([10, 9, 8, 7])
    is_super, drift = is_supermartingale(supermartingale)
    assert is_super
    assert drift < 0

    # Sequence with positive drift
    submartingale = np.array([7, 8, 9, 10])
    is_super, drift = is_supermartingale(submartingale)
    assert not is_super
    assert drift > 0

    # Martingale (zero drift)
    martingale = np.array([5, 5, 5, 5])
    is_super, drift = is_supermartingale(martingale)
    assert is_super
    assert drift == 0
