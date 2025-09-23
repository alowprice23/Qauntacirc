import pytest
import numpy as np
import random
import string
from math_utils.kolmogorov_bounds import (
    KolmogorovApproximator,
    minimum_description_length,
    normalized_compression_distance,
    algorithmic_probability_bound
)

def test_kolmogorov_complexity_approximation():
    approximator = KolmogorovApproximator()
    # A highly compressible string
    s_simple = "a" * 1000
    k_simple = approximator.approximate(s_simple)
    assert k_simple < 50  # Should be very small

    # A less compressible (random) string
    s_random = ''.join(random.choices(string.ascii_letters + string.digits, k=1000))
    k_random = approximator.approximate(s_random)
    assert k_random > 700 # Should be close to the original size

    # Check bytes vs string
    assert k_simple == approximator.approximate(s_simple.encode('utf-8'))

def test_minimum_description_length():
    # L(M) = 10 bits, L(D|M) = 100 bits -> MDL = 110
    assert minimum_description_length(10, 100) == 110
    assert minimum_description_length(0, 50) == 50

def test_normalized_compression_distance():
    s1 = "the quick brown fox jumps over the lazy dog"
    s2 = "the quick brown fox jumps over the lazy dog"
    # NCD of identical strings should be close to 0
    assert normalized_compression_distance(s1, s2) < 0.1

    s3 = ''.join(random.choices(string.ascii_letters, k=100))
    # NCD of unrelated strings should be close to 1
    assert normalized_compression_distance(s1, s3) > 0.7

    # Test with empty strings
    assert normalized_compression_distance("", "") == 0.0

def test_algorithmic_probability_bound():
    s_simple = "a" * 100
    p_simple = algorithmic_probability_bound(s_simple)
    assert 0 <= p_simple <= 1

    s_random = ''.join(random.choices(string.ascii_letters, k=100))
    p_random = algorithmic_probability_bound(s_random)
    assert 0 <= p_random <= 1

    # A more complex string should have a lower algorithmic probability
    assert p_random < p_simple
