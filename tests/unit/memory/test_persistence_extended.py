import pytest
import pickle
from pathlib import Path
import tempfile
from unittest.mock import MagicMock

from memory.persistence import DurableMemoryStore, CorruptedBackupError, InconsistentMemoryStateError
from memory.constellation import ConstellationMemory
from memory.types import ConstellationConfig

class InconsistentConstellationMemory(ConstellationMemory):
    """A ConstellationMemory subclass that is always inconsistent."""
    def verify_complete_consistency(self) -> MagicMock:
        return MagicMock(valid=False, violations=["test violation"])

@pytest.fixture
def memory_store():
    """Provides a DurableMemoryStore instance with a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield DurableMemoryStore(storage_path=Path(tmpdir))

def test_deserialize_wrong_type(memory_store: DurableMemoryStore):
    """Tests that deserializing an object of the wrong type raises an error."""
    dummy_object = {"key": "value"}
    serialized_dummy = pickle.dumps(dummy_object)

    with pytest.raises(TypeError):
        memory_store._deserialize_with_verification(serialized_dummy, ConstellationMemory)

def test_backup_corruption(memory_store: DurableMemoryStore):
    """Tests that a corrupted backup raises an error."""
    # Create a dummy backup file
    backup_id = "corrupted_backup.pkl"
    backup_file = memory_store.storage_path / backup_id

    backup_content = {
        "data": b"some data",
        "hash": "correct_hash",
        "consistency_proof": "proof"
    }
    with open(backup_file, "wb") as f:
        pickle.dump(backup_content, f)

    # The hash of "some data" is not "correct_hash", so this should fail
    with pytest.raises(CorruptedBackupError):
        memory_store.restore_memory_state(backup_id, ConstellationMemory)

def test_consistency_proof_storage(memory_store: DurableMemoryStore, constellation_memory: ConstellationMemory):
    """Tests that the consistency proof is stored and retrieved correctly."""
    proof = constellation_memory.generate_consistency_proof()

    # Persist the state
    result = memory_store.persist_memory_state(constellation_memory)

    # Retrieve the backup data directly to check the proof
    backup_data = memory_store.backup_manager.retrieve_backup(result.backup_id)

    assert backup_data["consistency_proof"] == proof

def test_inconsistent_restored_state(memory_store: DurableMemoryStore):
    """Tests that restoring an inconsistent memory state raises an error."""
    config = ConstellationConfig(
        neo4j_uri="bolt://localhost:7687",
        embedding_dimension=4,
        database_path=":memory:"
    )
    inconsistent_memory = InconsistentConstellationMemory(config)

    # Persist the inconsistent state
    result = memory_store.persist_memory_state(inconsistent_memory)

    with pytest.raises(InconsistentMemoryStateError):
        memory_store.restore_memory_state(result.backup_id, InconsistentConstellationMemory)
