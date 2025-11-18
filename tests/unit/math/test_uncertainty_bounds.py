import pytest
import numpy as np
from math_utils.uncertainty_bounds import (
    hoeffding_inequality,
    chernoff_bound_bernoulli,
    bennett_inequality,
    bootstrap_confidence_interval,
    UncertaintyQuantifier,
    ConfidenceBounds
)

def test_hoeffding_inequality():
    # P(|S_n/n - E[X]| >= t) <= 2 * exp(-2 * n * t^2 / (b-a)^2)
    # For Bernoulli(0.5), a=0, b=1. n=100, t=0.1
    # Bound = 2 * exp(-2 * 100 * 0.1^2 / 1^2) = 2 * exp(-2) = 0.27
    bound = hoeffding_inequality(n=100, t=0.1, bounds=(0, 1))
    assert bound == pytest.approx(2 * np.exp(-2))

    # Test with data
    data = np.random.normal(0, 1, 100)
    bound_data = hoeffding_inequality(n=100, t=0.1, data=data)
    assert 0 < bound_data <= 2.0

def test_chernoff_bound_bernoulli():
    # P(S_n >= a*n) <= exp(-n * D(a || p))
    # n=100, p=0.5, a=0.6
    # D(0.6 || 0.5) = 0.6*log(1.2) + 0.4*log(0.8) = 0.020
    # Bound = exp(-100 * 0.020) = exp(-2) = 0.135
    bound = chernoff_bound_bernoulli(n=100, p=0.5, a=0.6)
    kl_div = 0.6 * np.log(1.2) + 0.4 * np.log(0.8)
    assert bound == pytest.approx(np.exp(-100 * kl_div))

    # Should be 1 if a <= p
    assert chernoff_bound_bernoulli(n=100, p=0.5, a=0.5) == 1.0

def test_bennett_inequality():
    # P(S_n/n - E[X] >= t) <= exp(-n*sigma^2/b^2 * h(b*t/sigma^2))
    # n=100, t=0.1, sigma_sq=0.25, b=1
    n, t, sigma_sq, b = 100, 0.1, 0.25, 1.0
    nu = n * sigma_sq / b**2
    u = b * t / sigma_sq
    def h(u): return (1 + u) * np.log(1 + u) - u
    expected_bound = np.exp(-nu * h(u))
    assert bennett_inequality(n, t, sigma_sq, b) == pytest.approx(expected_bound)

def test_bootstrap_confidence_interval():
    np.random.seed(42) # for reproducibility
    data = np.random.normal(loc=10, scale=2, size=200)
    lower, upper = bootstrap_confidence_interval(data, n_bootstrap=1000)
    # The true mean 10 should be within the interval with high probability
    assert lower < 10 < upper
    assert lower < upper

from scipy.stats import norm

def test_uncertainty_quantifier():
    data = np.array([1, 2, 3, 4, 5])
    uq = UncertaintyQuantifier(data)
    assert uq.n == 5
    assert uq.mean == 3.0
    assert uq.std_dev == pytest.approx(np.sqrt(2))

    lower, upper = uq.get_confidence_bounds(confidence_level=0.95)
    z_score = norm.ppf(1 - 0.05 / 2)
    margin = z_score * np.sqrt(2) / np.sqrt(5)
    assert lower == pytest.approx(3.0 - margin)
    assert upper == pytest.approx(3.0 + margin)

def test_confidence_bounds():
    bounds = ConfidenceBounds(lower=1.23, upper=4.56)
    assert bounds.lower == 1.23
    assert bounds.upper == 4.56
    assert "lower=1.2300" in repr(bounds)
    assert "upper=4.5600" in repr(bounds)
