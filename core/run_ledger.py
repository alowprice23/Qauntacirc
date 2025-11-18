# core/run_ledger.py

"""
Manages and stores records of system execution runs.

This module provides a ledger for tracking all analysis runs performed by the
Orchestrator, allowing for persistence, retrieval, and analysis of past results.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from core.types import RunRecord

class RunLedger:
    """
    A ledger for managing and persisting `RunRecord` objects.
    """

    def __init__(self, storage_path: Path | str):
        """
        Initializes the RunLedger.

        Args:
            storage_path: The directory path where run records will be stored.
        """
        self.storage_path = Path(storage_path)
        # Ensure the storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def add_record(self, record: RunRecord):
        """
        Adds a new run record to the ledger and persists it to a file.

        The record is saved as a JSON file named after its `run_id`.

        Args:
            record: The RunRecord to add.
        """
        file_path = self.storage_path / f"{record.run_id}.json"

        # Use Pydantic's serialization capabilities
        # The default json encoder in pydantic handles UUID, datetime, etc.
        json_data = record.model_dump_json(indent=4)

        with open(file_path, 'w') as f:
            f.write(json_data)

    def get_record(self, run_id: UUID) -> Optional[RunRecord]:
        """
        Retrieves a specific run record by its ID.

        Args:
            run_id: The UUID of the run record to retrieve.

        Returns:
            The `RunRecord` object if found, otherwise None.
        """
        file_path = self.storage_path / f"{run_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            # Pydantic v2 can parse directly from a file or string
            return RunRecord.model_validate_json(f.read())

    def list_records(self) -> List[UUID]:
        """
        Lists the IDs of all run records stored in the ledger.

        Returns:
            A list of UUIDs for all available run records.
        """
        record_ids = []
        for file_path in self.storage_path.glob("*.json"):
            try:
                run_id = UUID(file_path.stem)
                record_ids.append(run_id)
            except ValueError:
                # Ignore files that are not named with a valid UUID
                continue
        return record_ids

    def get_all_records(self) -> List[RunRecord]:
        """
        Retrieves all run records from the ledger.

        Warning: This can be memory-intensive if there are many records.

        Returns:
            A list of all `RunRecord` objects.
        """
        all_records = []
        for run_id in self.list_records():
            record = self.get_record(run_id)
            if record:
                all_records.append(record)
        return all_records

# Example Usage
if __name__ == '__main__':
    from uuid import uuid4
    from datetime import datetime
    from core.types import QCState, SoftwareState, EnergyComponents

    # Create a dummy ledger in a temporary directory
    temp_dir = Path("./temp_ledger_storage")
    ledger = RunLedger(temp_dir)
    print(f"Ledger storage path: {ledger.storage_path.resolve()}")

    # Create a dummy record
    initial_state = QCState(
        id=uuid4(),
        timestamp=datetime.utcnow(),
        software_state=SoftwareState(component_versions={}, config_hashes={}, status="nominal"),
        energy=100.0,
        energy_components=EnergyComponents(static=50, dynamic=30, interaction=20),
        lyapunov_potential=0.5,
        contraction_factor=0.9,
        optimization_phase="A"
    )
    final_state = initial_state.model_copy(update={'energy': 80.0, 'lyapunov_potential': 0.4})

    record = RunRecord(
        run_id=uuid4(),
        start_time=initial_state.timestamp,
        end_time=datetime.utcnow(),
        status="completed",
        initial_state=initial_state,
        final_state=final_state,
        results=[]
    )

    # Add and retrieve the record
    ledger.add_record(record)
    print(f"\nAdded record with ID: {record.run_id}")

    retrieved_record = ledger.get_record(record.run_id)
    if retrieved_record:
        print(f"Successfully retrieved record. Final energy: {retrieved_record.final_state.energy}")
        assert retrieved_record.run_id == record.run_id

    # List records
    all_ids = ledger.list_records()
    print(f"\nAll record IDs in ledger: {all_ids}")
    assert record.run_id in all_ids

    # Clean up the temporary directory
    import shutil
    shutil.rmtree(temp_dir)
    print(f"\nCleaned up temporary directory: {temp_dir}")
