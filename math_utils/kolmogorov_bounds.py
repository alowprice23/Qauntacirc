import zlib
import gzip
import bz2
import lzma
import numpy as np

def multi_compressor_bound(data: bytes) -> int:
    """
    Approximates Kolmogorov complexity using the best of multiple compressors.
    This provides a tighter upper bound on K(x) than a single compressor.
    K(x) <= min(len(C1(x)), len(C2(x)), ...) + c

    Args:
        data: The data to compress, as a bytes object.

    Returns:
        The minimum compressed size in bytes.
    """
    if not isinstance(data, bytes):
        raise TypeError("Input data must be bytes.")

    return min(
        len(gzip.compress(data)),
        len(bz2.compress(data)),
        len(lzma.compress(data))
    )

def kolmogorov_complexity_approximation(data):
    """
    Approximates the Kolmogorov complexity of a string or bytes-like object
    by using the length of its compressed version.

    Kolmogorov complexity K(s) is the length of the shortest program that
    produces s as output. It is uncomputable. However, it can be approximated
    from above by the length of a compressed version of s, i.e., K(s) <= |C(s)|,
    where C is a standard compressor like zlib.

    Args:
        data (str or bytes): The data to analyze.

    Returns:
        int: The approximate Kolmogorov complexity in bytes.
    """
    if isinstance(data, str):
        data = data.encode('utf-8')

    return len(zlib.compress(data))

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

    c_s1 = len(zlib.compress(s1))
    c_s2 = len(zlib.compress(s2))
    c_s1s2 = len(zlib.compress(s1 + s2))

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
    k_s = kolmogorov_complexity_approximation(s)

    # The result is in bytes, so we convert to bits for the probability calculation.
    k_s_bits = k_s * 8

    return 2**(-k_s_bits)
