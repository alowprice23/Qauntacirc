# tests/unit/agents/pauli_guard/test_similarity_ops.py
"""
Tests for the PauliGuard similarity and orthogonalization operations.
"""

import pytest
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from agents.pauli_guard import similarity_ops

class TestPauliGuardSimilarityOps:
    """Test similarity and orthogonalization operations."""

    def test_ncd_similarity(self):
        """
        Test Normalized Compression Distance similarity.
        """
        code1 = "def f(x): return x + 1"
        code2 = "def g(y): return y + 1"
        code3 = "class MyClass: pass"

        # Similarity should be high for semantically similar code
        sim_12 = similarity_ops.ncd_similarity(code1, code2)
        assert sim_12 > 0.5

        # Similarity should be low for different code
        sim_13 = similarity_ops.ncd_similarity(code1, code3)
        assert sim_13 < 0.5

        # Test edge cases
        assert similarity_ops.ncd_similarity("", "") == 1.0
        assert similarity_ops.ncd_similarity(code1, "") == 0.0

    def test_gram_schmidt_orthogonalization(self):
        """
        Test Gram-Schmidt orthogonalization for code vectors.
        """
        # Two similar "documents" (code blocks)
        doc1 = "the cat sat on the mat"
        doc2 = "the cat sat on the mat and the dog stood by"

        # A different document
        doc3 = "the quick brown fox jumps over the lazy dog"

        vectorizer = TfidfVectorizer()
        code_vectors = vectorizer.fit_transform([doc1, doc2, doc3]).toarray()

        # Ensure we have non-zero vectors
        assert np.any(code_vectors)

        orthogonal_basis, _ = similarity_ops.gram_schmidt_orthogonalize(code_vectors)

        # Check that the basis vectors are orthogonal
        # The dot product of any two different basis vectors should be close to 0
        for i in range(orthogonal_basis.shape[0]):
            for j in range(i + 1, orthogonal_basis.shape[0]):
                dot_product = np.dot(orthogonal_basis[i], orthogonal_basis[j])
                assert abs(dot_product) < 1e-9, f"Vectors {i} and {j} are not orthogonal: dot product is {dot_product}"

        # Check that the basis vectors are unit vectors (have a norm of ~1)
        for i in range(orthogonal_basis.shape[0]):
            norm = np.linalg.norm(orthogonal_basis[i])
            # The last vector can be a zero vector if the original set is linearly dependent
            if np.any(orthogonal_basis[i]):
                 assert np.isclose(norm, 1.0), f"Vector {i} is not a unit vector: norm is {norm}"
