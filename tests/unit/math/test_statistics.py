import pytest
import numpy as np
from math_utils.statistics import (
    robust_mean,
    t_test_one_sample,
    mann_whitney_u_test,
    bonferroni_correction,
    fdr_correction,
    bootstrap,
    jackknife_estimate
)

def test_robust_mean():
    data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert robust_mean(data, trim_fraction=0.1) == np.mean([2, 3, 4, 5, 6, 7, 8, 9])

    data_with_outliers = np.array([1, 2, 3, 4, 5, 100])
    assert robust_mean(data_with_outliers, trim_fraction=0.2) < np.mean(data_with_outliers)

def test_t_test_one_sample():
    data = np.random.normal(loc=10, scale=1, size=100)
    # Test against a different mean -> small p-value
    stat, p_val = t_test_one_sample(data, popmean=5)
    assert p_val < 0.05
    # Test against the true mean -> large p-value
    stat, p_val = t_test_one_sample(data, popmean=10)
    assert p_val > 0.05

def test_mann_whitney_u_test():
    x = np.random.normal(loc=0, scale=1, size=100)
    y = np.random.normal(loc=1, scale=1, size=100)
    # Different distributions -> small p-value
    u_stat, p_val = mann_whitney_u_test(x, y)
    assert p_val < 0.05

    y_same = np.random.normal(loc=0, scale=1, size=100)
    # Same distribution -> large p-value
    u_stat, p_val = mann_whitney_u_test(x, y_same)
    assert p_val > 0.05

def test_bonferroni_correction():
    p_values = [0.01, 0.02, 0.03, 0.5]
    corrected = bonferroni_correction(p_values)
    expected = [0.04, 0.08, 0.12, 1.0]
    assert np.allclose(corrected, expected)

def test_fdr_correction():
    p_values = [0.001, 0.005, 0.01, 0.05, 0.1]
    significant_indices = fdr_correction(p_values, alpha=0.05)
    # With alpha=0.05, the first 3 should be significant
    assert len(significant_indices) == 3

def test_bootstrap():
    data = np.array([1, 2, 3, 4, 5])
    bootstrap_means = bootstrap(data, n_bootstrap=500)
    assert len(bootstrap_means) == 500
    # The mean of bootstrap means should be close to the sample mean
    assert np.mean(bootstrap_means) == pytest.approx(np.mean(data), abs=0.1)

def test_jackknife_estimate():
    data = np.array([1, 2, 3, 4, 5])
    # For the mean, jackknife estimate is the sample mean, and bias is 0
    est, bias, var = jackknife_estimate(data, func=np.mean)
    assert est == pytest.approx(np.mean(data))
    assert bias == pytest.approx(0.0)
    assert var > 0
