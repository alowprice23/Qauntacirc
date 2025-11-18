import pytest
import numpy as np
from math_utils.distance_metrics import (
    euclidean_distance,
    manhattan_distance,
    minkowski_distance,
    levenshtein_distance,
    wasserstein_1d_distance,
    hausdorff_distance,
    software_similarity_metric
)

def test_euclidean_distance():
    u = np.array([0, 0])
    v = np.array([3, 4])
    assert euclidean_distance(u, v) == pytest.approx(5.0)

def test_manhattan_distance():
    u = np.array([0, 0])
    v = np.array([3, 4])
    assert manhattan_distance(u, v) == pytest.approx(7.0)

def test_minkowski_distance():
    u = np.array([0, 0])
    v = np.array([3, 4])
    assert minkowski_distance(u, v, p=3) == pytest.approx(pow(3**3 + 4**3, 1/3))

def test_levenshtein_distance():
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("saturday", "sunday") == 3
    assert levenshtein_distance("a", "b") == 1
    assert levenshtein_distance("a", "a") == 0
    assert levenshtein_distance("", "a") == 1

def test_wasserstein_1d_distance():
    u = np.array([0, 1, 3])
    v = np.array([5, 6, 8])
    # For 1D, it's the integral of the |CDF_u(x) - CDF_v(x)| dx
    # With scipy, it's the sum of |u_sorted[i] - v_sorted[i]| / n
    # But for direct values, it's just the mean absolute difference
    # Let's test with scipy's implementation detail for sorted arrays
    from scipy.stats import wasserstein_distance
    assert wasserstein_1d_distance(u, v) == wasserstein_distance(u, v)

def test_hausdorff_distance():
    u = np.array([[1, 2], [3, 4], [5, 6]])
    v = np.array([[1, 2], [3, 5], [5, 7]])
    dist = hausdorff_distance(u, v)
    assert dist > 0
    assert hausdorff_distance(u, u) == 0

def test_software_similarity_metric():
    state1 = {
        'code_str': 'def f(x): return x',
        'dep_vector': np.array([1, 0, 0])
    }
    state2 = {
        'code_str': 'def g(y): return y',
        'dep_vector': np.array([0, 1, 0])
    }
    dist = software_similarity_metric(state1, state2)
    assert dist > 0

    dist_same = software_similarity_metric(state1, state1)
    # Since dep_vector is empty, dist should be 0
    state_no_dep = {'code_str': 'a'}
    dist_no_dep = software_similarity_metric(state_no_dep, state_no_dep, weights={'code_structure':1.0, 'dependencies':0.0})
    assert dist_no_dep == 0.0
