import zlib
import numpy as np
from core.compression import MultiCompressor

class KolmogorovApproximator:
    """
    Approximates Kolmogorov complexity using a multi-compressor approach.
    """
    def __init__(self):
        self.compressor = MultiCompressor()

    def approximate(self, data: str | bytes) -> int:
        """
        Approximates the Kolmogorov complexity of a string or bytes-like object.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        k_approx = self.compressor.get_best_compression_size(data)
        self.validate_bounds(k_approx, data)
        return k_approx

    def validate_bounds(self, k_approx: int, data: bytes):
        """
        Performs a basic sanity check based on Bennett-Gács deviation bounds.
        Since K(x) is uncomputable, we can't directly check the bound.
        Instead, we check if K_approx is within a plausible range.
        A simple check is that K_approx should not be much larger than the
        original data length.
        """
        data_len = len(data)
        # The compressed size should not be significantly larger than the original size.
        # We add a small constant to account for overhead.
        if k_approx > data_len + 100: # 100 is an arbitrary but reasonable constant
            raise ValueError("Kolmogorov approximation is implausibly large.")

def minimum_description_length(model_description_length, data_description_length):
    """
    Calculates the Minimum Description Length (MDL) for a model given some data.

    MDL(M, D) = L(M) + L(D|M)
    where L(M) is the length of the description of the model, and
    L(D|M) is the length of the description of the data given the model.

    This function simply sums the two lengths. The caller is responsible for
    determining the appropriate description lengths based on their chosen
    encoding scheme. For example, L(D|M) is often taken as the negative
    log-likelihood of the data given the model.

    Args:
        model_description_length (float): The description length of the model, L(M).
        data_description_length (float): The description length of the data given the model, L(D|M).

    Returns:
        float: The MDL score.
    """
    return model_description_length + data_description_length

def normalized_compression_distance(s1, s2):
    """
    Calculates the Normalized Compression Distance (NCD), a similarity metric
    based on Kolmogorov complexity.

    NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))

    Args:
        s1 (str or bytes): The first string.
        s2 (str or bytes): The second string.

    Returns:
        float: The NCD, a value between 0 and 1 (approximately).
    """
    if isinstance(s1, str):
        s1 = s1.encode('utf-8')
    if isinstance(s2, str):
        s2 = s2.encode('utf-8')

    approximator = KolmogorovApproximator()
    c_s1 = approximator.approximate(s1)
    c_s2 = approximator.approximate(s2)
    c_s1s2 = approximator.approximate(s1 + s2)

    if max(c_s1, c_s2) == 0:
        return 0.0

    return (c_s1s2 - min(c_s1, c_s2)) / max(c_s1, c_s2)

def algorithmic_probability_bound(s):
    """
    Illustrates the concept of Algorithmic Probability (Solomonoff Induction).

    The algorithmic probability P(s) of a string s is the sum of probabilities of
    all programs that produce s. P(s) = sum_{p: U(p)=s} 2^(-|p|). This is the
    cornerstone of Solomonoff's theory of induction but is uncomputable.

    A key result is that P(s) is approximately 2^(-K(s)), where K(s) is the
    Kolmogorov complexity of s. This function uses that approximation.

    Args:
        s (str or bytes): The string for which to estimate the algorithmic probability.

    Returns:
        float: An upper bound on the algorithmic probability of the string.
    """
    # This is a conceptual function. A real implementation is not computable.
    # We use the approximation P(s) approx= 2^(-K(s)).
    approximator = KolmogorovApproximator()
    k_s = approximator.approximate(s)

    # The result is in bytes, so we convert to bits for the probability calculation.
    k_s_bits = k_s * 8

    return 2**(-k_s_bits)
