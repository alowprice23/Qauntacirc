import pytest
import numpy as np
from memory.vector_space import QuantumVectorSpace, InvalidVectorError
from memory.types import VectorMetadata

@pytest.fixture
def vector_space():
    """Provides a QuantumVectorSpace instance for testing."""
    return QuantumVectorSpace(dimension=4)

def test_add_invalid_dimension(vector_space: QuantumVectorSpace):
    """Tests adding a vector with an invalid dimension."""
    vector = np.array([1.0, 0.0, 0.0]) # 3 dimensions, expected 4
    metadata = VectorMetadata(fact_id="fact1", type="test", timestamp="now", mathematical_hash="hash1")
    with pytest.raises(InvalidVectorError):
        vector_space.add_vector(vector, metadata)

def test_add_unnormalized_vector(vector_space: QuantumVectorSpace):
    """Tests that adding an unnormalized vector works and it gets normalized."""
    vector = np.array([2.0, 0.0, 0.0, 0.0])
    metadata = VectorMetadata(fact_id="fact1", type="test", timestamp="now", mathematical_hash="hash1")
    vector_id = vector_space.add_vector(vector, metadata)

    # Retrieve the vector from faiss index
    retrieved_vector = vector_space.index.reconstruct(vector_id.id)
    assert np.isclose(np.linalg.norm(retrieved_vector), 1.0)

def test_math_structure_update(vector_space: QuantumVectorSpace):
    """Tests that the mathematical structure is updated when adding vectors."""
    assert vector_space.mathematical_structure.vector_count == 0

    vec1 = np.array([1.0, 0.0, 0.0, 0.0])
    meta1 = VectorMetadata(fact_id="fact1", type="test", timestamp="now", mathematical_hash="hash1")
    vector_space.add_vector(vec1, meta1)

    assert vector_space.mathematical_structure.vector_count == 1
    assert np.allclose(vector_space.mathematical_structure.mean_vector, vec1 / np.linalg.norm(vec1))

    vec2 = np.array([0.0, 1.0, 0.0, 0.0])
    meta2 = VectorMetadata(fact_id="fact2", type="test", timestamp="now", mathematical_hash="hash2")
    vector_space.add_vector(vec2, meta2)

    assert vector_space.mathematical_structure.vector_count == 2
    expected_mean = (vec1 / np.linalg.norm(vec1) + vec2 / np.linalg.norm(vec2)) / 2
    assert np.allclose(vector_space.mathematical_structure.mean_vector, expected_mean)

def test_search_result_properties(vector_space: QuantumVectorSpace):
    """Tests that the search result contains all the required properties."""
    vec1 = np.array([1.0, 0.1, 0.2, 0.3])
    meta1 = VectorMetadata(fact_id="fact1", type="test", timestamp="now", mathematical_hash="hash1")
    vector_space.add_vector(vec1, meta1)

    query_vector = np.array([0.9, 0.0, 0.0, 0.0])
    results = vector_space.search_similar(query_vector, k=1, threshold=0.5)

    assert len(results.matches) == 1
    match = results.matches[0]

    assert match.mathematical_certificate.startswith("cert_")
    assert results.query_hash is not None
    assert "mean_similarity" in results.mathematical_bounds
    assert results.information_content is not None

def test_information_content_calculation(vector_space: QuantumVectorSpace):
    """Tests the information content calculation."""
    # Add two identical vectors
    vec1 = np.array([1.0, 0.0, 0.0, 0.0])
    meta1 = VectorMetadata(fact_id="fact1", type="test", timestamp="now", mathematical_hash="hash1")
    vector_space.add_vector(vec1, meta1)
    vector_space.add_vector(vec1, meta1)

    # Search for them
    results = vector_space.search_similar(vec1, k=2, threshold=0.9)

    # With two identical similarities, the distribution is uniform, entropy should be log2(2) = 1.0
    assert np.isclose(results.information_content, 1.0)

    # Add another, different vector
    vec2 = np.array([0.0, 1.0, 0.0, 0.0])
    meta2 = VectorMetadata(fact_id="fact2", type="test", timestamp="now", mathematical_hash="hash2")
    vector_space.add_vector(vec2, meta2)

    results = vector_space.search_similar(np.array([0.8, 0.2, 0.0, 0.0]), k=3, threshold=0.1)
    # The entropy should be higher than 0 and strictly less than log2(3) because the similarities are not equal
    assert results.information_content > 0
    assert results.information_content < np.log2(3)
