import pickle
import hashlib
from pathlib import Path
from typing import Any, TYPE_CHECKING, Dict

from memory.types import PersistenceResult

if TYPE_CHECKING:
    from memory.constellation import ConstellationMemory

class CorruptedBackupError(Exception):
    """Raised when a backup is corrupted or integrity check fails."""
    pass

class InconsistentMemoryStateError(Exception):
    """Raised when a restored memory state fails consistency checks."""
    pass

class CryptographicIntegrityChecker:
    """A simple cryptographic integrity checker using SHA256."""
    def compute_hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def verify_integrity(self, data: bytes, expected_hash: str) -> Dict[str, Any]:
        """Verifies the integrity of the data using its hash."""
        actual_hash = self.compute_hash(data)
        if actual_hash == expected_hash:
            return {"valid": True}
        else:
            return {"valid": False, "violations": [f"Hash mismatch: expected {expected_hash}, got {actual_hash}"]}

class BackupManager:
    """Manages the storage and retrieval of backups."""
    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, data: bytes, integrity_hash: str, mathematical_consistency_proof: str) -> Dict[str, Any]:
        """Creates a new backup, including the mathematical consistency proof."""
        backup_id = f"backup_{integrity_hash[:12]}.pkl"
        backup_file = self.backup_dir / backup_id

        backup_content = {
            "data": data,
            "hash": integrity_hash,
            "consistency_proof": mathematical_consistency_proof
        }
        with open(backup_file, "wb") as f:
            pickle.dump(backup_content, f)

        return {
            "success": True,
            "backup_id": backup_id,
            "mathematical_verification": "Proof stored in backup."
        }

    def retrieve_backup(self, backup_id: str) -> Dict[str, Any]:
        """Retrieves a backup, including its consistency proof."""
        backup_file = self.backup_dir / backup_id
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup with ID '{backup_id}' not found in {self.backup_dir}")

        with open(backup_file, "rb") as f:
            content = pickle.load(f)

        return {
            "serialized_state": content["data"],
            "integrity_hash": content["hash"],
            "consistency_proof": content.get("consistency_proof", "N/A")
        }

class DurableMemoryStore:
    """
    Manages the durable persistence and recovery of the constellation memory state,
    with cryptographic integrity and mathematical consistency checks.
    """
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.integrity_checker = CryptographicIntegrityChecker()
        self.backup_manager = BackupManager(self.storage_path)

    def _serialize_with_mathematical_verification(self, constellation: 'ConstellationMemory') -> bytes:
        """Serializes the constellation memory state using pickle."""
        # Note: A production system might need a more robust serialization method.
        serialized_state = pickle.dumps(constellation)
        if not serialized_state:
            raise ValueError("Serialization resulted in empty data.")
        return serialized_state

    def _deserialize_with_verification(self, serialized_state: bytes, constellation_class: type) -> 'ConstellationMemory':
        """Deserializes the constellation memory state and verifies its type."""
        restored_obj = pickle.loads(serialized_state)
        if not isinstance(restored_obj, constellation_class):
            raise TypeError(f"Deserialized object is not of the expected type. Got {type(restored_obj)}, expected {constellation_class}")
        return restored_obj

    def persist_memory_state(self, constellation: 'ConstellationMemory') -> PersistenceResult:
        """
        Persists the memory state with cryptographic integrity and mathematical consistency.
        """
        serialized_state = self._serialize_with_mathematical_verification(constellation)
        integrity_hash = self.integrity_checker.compute_hash(serialized_state)
        consistency_proof = constellation.generate_consistency_proof()

        backup_result = self.backup_manager.create_backup(
            data=serialized_state,
            integrity_hash=integrity_hash,
            mathematical_consistency_proof=consistency_proof
        )

        return PersistenceResult(
            success=backup_result["success"],
            backup_id=backup_result["backup_id"],
            integrity_hash=integrity_hash,
            mathematical_verification=backup_result["mathematical_verification"]
        )

    def restore_memory_state(self, backup_id: str, constellation_class: type) -> 'ConstellationMemory':
        """
        Restores the memory state with integrity verification and consistency checking.
        """
        backup_data = self.backup_manager.retrieve_backup(backup_id)

        integrity_verification = self.integrity_checker.verify_integrity(
            backup_data["serialized_state"], backup_data["integrity_hash"]
        )
        if not integrity_verification["valid"]:
            raise CorruptedBackupError(f"Backup integrity verification failed: {integrity_verification['violations']}")

        restored_constellation = self._deserialize_with_verification(backup_data["serialized_state"], constellation_class)

        # Verify that the restored state is consistent
        consistency_check = restored_constellation.verify_complete_consistency()
        if not consistency_check.valid:
            raise InconsistentMemoryStateError(f"Restored memory state is mathematically inconsistent: {consistency_check.violations}")

        # Optional: Verify the stored proof against a re-calculated one
        # new_proof = restored_constellation.generate_consistency_proof()
        # if new_proof != backup_data["consistency_proof"]:
        #     warnings.warn("Restored state's consistency proof does not match the backed-up proof.")

        return restored_constellation
