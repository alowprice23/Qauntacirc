import pytest
from unittest.mock import MagicMock

from memory.context import ContextAssemblyEngine
from memory.constellation import ConstellationMemory
from memory.types import ConstellationConfig, ConstellationResult, Fact, FactNode, OptimalEncoding, FactType

import numpy as np

@pytest.fixture
def mock_constellation_memory():
    """Provides a mocked ConstellationMemory instance."""
    memory = MagicMock(spec=ConstellationMemory)

    # Mock the return value of query_facts
    mock_fact = Fact(content="Test fact", type=FactType.PROPOSITION, confidence=0.9)
    mock_encoding = OptimalEncoding(algorithm='zstd', compressed_data=b'', compression_ratio=1.0, entropy=1.0, bound_verification={}, optimality_proof="", hash="hash")
    mock_embedding = np.random.rand(4) # Use a real numpy array
    mock_fact_node = FactNode(id="fact1", fact=mock_fact, encoding=mock_encoding, embedding=mock_embedding, storage_locations={})

    memory.query_facts.return_value = ConstellationResult(
        facts=[mock_fact_node],
        query_hash="qhash",
        mathematical_consistency={},
        information_content=1.0,
        retrieval_proof="proof"
    )
    return memory

def test_assemble_context(mock_constellation_memory):
    """Tests assembling a context."""
    engine = ContextAssemblyEngine(constellation=mock_constellation_memory)

    optimized_context = engine.assemble_context(query="test query", max_tokens=100)

    assert "Test fact" in optimized_context.context_text
    assert len(optimized_context.selected_facts) == 1
    assert optimized_context.selected_facts[0].content == "Test fact"
    assert optimized_context.token_usage > 0
