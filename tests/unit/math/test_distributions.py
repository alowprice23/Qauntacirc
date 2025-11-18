import pytest
import numpy as np
from scipy import stats
from math_utils.distributions import (
    Normal,
    Exponential,
    goodness_of_fit_kstest,
    bayesian_estimation_normal
)

def test_normal_distribution():
    mu, sigma = 5, 2
    dist = Normal(mu, sigma)
    assert dist.params['mu'] == mu
    assert dist.params['sigma'] == sigma

    # Test pdf
    x = 5
    expected_pdf = stats.norm.pdf(x, loc=mu, scale=sigma)
    assert dist.pdf(x) == pytest.approx(expected_pdf)

    # Test cdf
    expected_cdf = stats.norm.cdf(x, loc=mu, scale=sigma)
    assert dist.cdf(x) == pytest.approx(expected_cdf)

    # Test sample
    samples = dist.sample(100)
    assert len(samples) == 100
    assert np.mean(samples) == pytest.approx(mu, abs=1.0)

def test_normal_fit_mle():
    data = np.random.normal(loc=10, scale=3, size=1000)
    fitted_dist = Normal.fit_mle(data)
    assert fitted_dist.params['mu'] == pytest.approx(10, abs=0.5)
    assert fitted_dist.params['sigma'] == pytest.approx(3, abs=0.5)

def test_exponential_distribution():
    lambd = 0.5
    dist = Exponential(lambd)
    assert dist.params['lambda'] == lambd

    # Test pdf
    x = 1
    expected_pdf = stats.expon.pdf(x, scale=1/lambd)
    assert dist.pdf(x) == pytest.approx(expected_pdf)

    # Test cdf
    expected_cdf = stats.expon.cdf(x, scale=1/lambd)
    assert dist.cdf(x) == pytest.approx(expected_cdf)

    # Test sample
    samples = dist.sample(100)
    assert len(samples) == 100
    assert np.mean(samples) == pytest.approx(1/lambd, abs=1.0)

def test_exponential_fit_mle():
    data = np.random.exponential(scale=2.0, size=1000) # scale = 1/lambda
    fitted_dist = Exponential.fit_mle(data)
    assert fitted_dist.params['lambda'] == pytest.approx(0.5, abs=0.1)

def test_goodness_of_fit_kstest():
    # Test with data that fits
    normal_data = np.random.normal(loc=0, scale=1, size=100)
    ks_stat, p_val = goodness_of_fit_kstest(normal_data, Normal)
    assert p_val > 0.05 # Should not reject the null hypothesis

    # Test with data that does not fit
    exp_data = np.random.exponential(scale=1, size=100)
    ks_stat, p_val = goodness_of_fit_kstest(exp_data, Normal)
    assert p_val < 0.05 # Should reject the null hypothesis

def test_bayesian_estimation_normal():
    np.random.seed(42)
    data = np.array([10, 11, 12, 11, 11.5])
    prior_mu, prior_sigma = 0, 10

    # Calculate the expected posterior mean analytically
    data_mean = np.mean(data)
    sigma_sq = np.var(data, ddof=1)
    n = len(data)
    prior_sigma_sq = prior_sigma**2

    expected_posterior_mu = ( (prior_mu / prior_sigma_sq) + (np.sum(data) / sigma_sq) ) / \
                            ( (1 / prior_sigma_sq) + (n / sigma_sq) )

    posterior_samples = bayesian_estimation_normal(data, prior_mu, prior_sigma, n_samples=2000)

    posterior_mean = np.mean(posterior_samples)

    # The mean of the samples should be close to the true posterior mean
    assert posterior_mean == pytest.approx(expected_posterior_mu, abs=0.1)
