import pytest
from memory.constellation import ConstellationMemory
from memory.types import ConstellationConfig, Fact, FactType

@pytest.fixture
def constellation_memory():
    """Provides a ConstellationMemory instance for testing."""
    config = ConstellationConfig(
        neo4j_uri="bolt://localhost:7687",
        embedding_dimension=4,
        database_path=":memory:"
    )
    # Reducing the embedding dimension for the test
    memory = ConstellationMemory(config)
    memory.vector_store.dimension = 4
    return memory

def test_store_fact(constellation_memory: ConstellationMemory):
    """Tests storing a fact in the constellation memory."""
    fact = Fact(
        content="The Earth is round.",
        type=FactType.PROPOSITION
    )

    fact_node = constellation_memory.store_fact(fact)

    assert fact_node is not None
    assert fact_node.fact.content == "The Earth is round."
    assert "graph" in fact_node.storage_locations
    assert "vector" in fact_node.storage_locations
    assert "metadata" in fact_node.storage_locations

    # Check if vector was added
    assert constellation_memory.vector_store.index.ntotal == 1
