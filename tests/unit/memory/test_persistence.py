import pytest
from pathlib import Path
import tempfile

from memory.persistence import DurableMemoryStore
from memory.constellation import ConstellationMemory
from memory.types import ConstellationConfig, Fact, FactType

@pytest.fixture
def memory_store():
    """Provides a DurableMemoryStore instance with a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield DurableMemoryStore(storage_path=Path(tmpdir))

@pytest.fixture
def constellation_memory():
    """Provides a fresh ConstellationMemory instance for testing."""
    config = ConstellationConfig(
        neo4j_uri="bolt://localhost:7687",
        embedding_dimension=4,
        database_path=":memory:"
    )
    return ConstellationMemory(config)

def test_persist_and_restore(memory_store: DurableMemoryStore, constellation_memory: ConstellationMemory):
    """Tests persisting and then restoring a ConstellationMemory instance."""
    # Add a fact to the memory to have some state
    test_fact = Fact(content="A fact to be persisted.", type=FactType.PROPOSITION)
    constellation_memory.store_fact(test_fact)

    # Persist the state
    result = memory_store.persist_memory_state(constellation_memory)
    assert result.success
    assert result.backup_id is not None

    # Restore the state
    restored_memory = memory_store.restore_memory_state(result.backup_id)

    # Check if the restored state is correct
    assert isinstance(restored_memory, ConstellationMemory)
    # This check is tricky because the in-memory stores are part of the object state
    # Let's check something simple, like the vector count
    assert restored_memory.vector_store.index.ntotal == 1
