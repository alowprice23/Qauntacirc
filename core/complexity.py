# core/complexity.py

"""
Calculates the complexity component of the energy function.
"""

from __future__ import annotations
import gzip
import bz2
import lzma
import numpy as np

from math_utils.info_entropy import shannon_entropy

class ComplexityCalculator:
    """
    Calculates complexity using a combination of Kolmogorov complexity approximation
    and Shannon entropy for semantic features.
    """
    def __init__(self):
        pass

    def _kolmogorov_approx(self, data: str) -> int:
        """
        Approximates Kolmogorov complexity using various compression algorithms.
        K_approx(x) ≈ min(|gzip(x)|, |bzip2(x)|, |lzma(x)|)
        """
        encoded_data = data.encode('utf-8')
        gzipped = len(gzip.compress(encoded_data))
        bzipped = len(bz2.compress(encoded_data))
        lzmaed = len(lzma.compress(encoded_data))
        return min(gzipped, bzipped, lzmaed)

    def calculate(self, code: str) -> float:
        """
        Calculates the complexity energy of a piece of code.
        E_complexity = Σᵢ [K_approx(mᵢ) + H(mᵢ)]
        """
        # For now, we'll treat the entire code as a single module.
        # A more advanced implementation would break it down into modules/functions.

        # Approximate Kolmogorov complexity
        k_approx = self._kolmogorov_approx(code)

        # Calculate Shannon entropy of the code's tokens
        # A simple whitespace-based tokenizer
        tokens = code.split()
        h_semantic = shannon_entropy(tokens)

        # The complexity energy is a combination of these two measures
        # The weighting can be adjusted based on empirical results
        return float(k_approx + h_semantic)
