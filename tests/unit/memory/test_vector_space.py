import pytest
import numpy as np
from memory.vector_space import QuantumVectorSpace
from memory.types import VectorMetadata

@pytest.fixture
def vector_space():
    """Provides a QuantumVectorSpace instance for testing."""
    return QuantumVectorSpace(dimension=4)

def test_add_vector(vector_space: QuantumVectorSpace):
    """Tests adding a vector to the space."""
    vector = np.array([1.0, 0.0, 0.0, 0.0])
    metadata = VectorMetadata(fact_id="fact1", type="test", timestamp="now", mathematical_hash="hash1")

    vector_id = vector_space.add_vector(vector, metadata)
    assert vector_id.id == 0
    assert vector_space.index.ntotal == 1

def test_search_similar(vector_space: QuantumVectorSpace):
    """Tests searching for similar vectors."""
    vec1 = np.array([1.0, 0.1, 0.2, 0.3])
    meta1 = VectorMetadata(fact_id="fact1", type="test", timestamp="now", mathematical_hash="hash1")
    vector_space.add_vector(vec1, meta1)

    vec2 = np.array([0.1, 1.0, 0.2, 0.3])
    meta2 = VectorMetadata(fact_id="fact2", type="test", timestamp="now", mathematical_hash="hash2")
    vector_space.add_vector(vec2, meta2)

    query_vector = np.array([0.9, 0.0, 0.0, 0.0])

    # Search for the most similar vector
    results = vector_space.search_similar(query_vector, k=1, threshold=0.5)

    assert len(results.matches) == 1
    assert results.matches[0].vector_id.id == 0 # vec1 is more similar
    assert results.matches[0].metadata.fact_id == "fact1"
