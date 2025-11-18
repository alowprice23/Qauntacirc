import pytest
import numpy as np
from scipy import stats
from math_utils.estimation import (
    maximum_likelihood_estimator,
    m_estimator,
    huber_psi,
    bias_variance_decomposition
)

def test_maximum_likelihood_estimator():
    # MLE for the mean of a normal distribution
    np.random.seed(42)
    data = np.random.normal(loc=5.0, scale=2.0, size=100)

    def log_likelihood_normal(params, data):
        mu = params[0]
        # Assuming sigma=2.0 is known
        return np.sum(stats.norm.logpdf(data, loc=mu, scale=2.0))

    initial_params = np.array([0.0])
    estimated_mu = maximum_likelihood_estimator(data, log_likelihood_normal, initial_params)

    assert estimated_mu[0] == pytest.approx(np.mean(data), abs=1e-3)

from math_utils.estimation import huber_rho

def test_m_estimator():
    np.random.seed(42)
    data = np.concatenate([np.random.normal(loc=5, scale=1, size=100), [50, 55]]) # With outliers

    estimated_loc = m_estimator(data, huber_rho, initial_param=0.0)

    # The M-estimate should be more robust to outliers than the mean
    assert np.abs(estimated_loc - 5) < np.abs(np.mean(data) - 5)

def test_huber_psi():
    assert huber_psi(1.0) == 1.0
    assert huber_psi(-1.0) == -1.0
    assert huber_psi(2.0, c=1.5) == 1.5
    assert huber_psi(-2.0, c=1.5) == -1.5

def test_bias_variance_decomposition():
    true_mean = 10.0

    def data_generator(n_samples):
        return np.random.normal(loc=true_mean, scale=2.0, size=n_samples)

    def estimator(data):
        return np.mean(data)

    bias_sq, variance, mse = bias_variance_decomposition(
        estimator, true_mean, data_generator, n_simulations=500
    )

    # For the sample mean of a normal distribution, the bias should be close to 0
    assert bias_sq == pytest.approx(0.0, abs=1e-2)
    # Check if MSE is close to bias^2 + variance
    assert mse == pytest.approx(bias_sq + variance, rel=1e-1)
