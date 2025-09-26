# core/persistence.py

"""
Manages the long-term storage and retrieval of system state and results.

This module provides a high-level interface for persisting all artifacts
related to a specific analysis run, including state snapshots, final results,
and configurations.
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID
from typing import TypeVar, Type, Optional
from datetime import datetime

import networkx as nx
from pydantic import BaseModel

from core.types import QCState, RunRecord
from core.serialization import save_model_to_json, load_model_from_json, NumpyJSONEncoder
from core.run_ledger import RunLedger
from memory.constellation import ConstellationMemory

T = TypeVar('T', bound=BaseModel)

class PersistenceManager:
    """
    Handles the storage and retrieval of all data for analysis runs.

    It organizes storage by creating a dedicated directory for each run,
    identified by a unique `run_id`.
    """

    def __init__(self, base_storage_path: Path | str):
        """
        Initializes the PersistenceManager.

        Args:
            base_storage_path: The root directory where all run data will be stored.
        """
        self.base_path = Path(base_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # The ledger for final run records can be managed here
        self.run_ledger = RunLedger(self.base_path / "run_records")

    def get_run_path(self, run_id: UUID) -> Path:
        """
        Gets the dedicated storage path for a given run ID.

        Args:
            run_id: The unique identifier for the run.

        Returns:
            The Path object for the run's directory.
        """
        run_path = self.base_path / "runs" / str(run_id)
        run_path.mkdir(parents=True, exist_ok=True)
        return run_path

    def save_snapshot(self, run_id: UUID, state: QCState, snapshot_name: str):
        """
        Saves a snapshot of a QCState during a run.

        Args:
            run_id: The ID of the run this snapshot belongs to.
            state: The QCState to save.
            snapshot_name: A unique name for the snapshot (e.g., "iteration_500" or "best_state").
        """
        run_path = self.get_run_path(run_id)
        snapshot_path = run_path / "snapshots"
        snapshot_path.mkdir(exist_ok=True)

        file_path = snapshot_path / f"{snapshot_name}.json"
        save_model_to_json(state, file_path)

    def load_snapshot(self, run_id: UUID, snapshot_name: str) -> Optional[QCState]:
        """
        Loads a previously saved QCState snapshot.

        Args:
            run_id: The ID of the run.
            snapshot_name: The name of the snapshot to load.

        Returns:
            The loaded QCState object, or None if not found.
        """
        run_path = self.get_run_path(run_id)
        file_path = run_path / "snapshots" / f"{snapshot_name}.json"

        if not file_path.exists():
            return None

        return load_model_from_json(file_path, QCState)

    def save_run_record(self, record: RunRecord):
        """
        Saves the final RunRecord using the managed RunLedger.

        Args:
            record: The final RunRecord of the analysis.
        """
        self.run_ledger.add_record(record)

    def load_run_record(self, run_id: UUID) -> Optional[RunRecord]:
        """
        Loads a final RunRecord by its ID.

        Args:
            run_id: The ID of the run to load the record for.

        Returns:
            The RunRecord if found, otherwise None.
        """
        return self.run_ledger.get_record(run_id)

    def save_artifact(self, run_id: UUID, content: str | bytes, artifact_name: str):
        """
        Saves a generic artifact (e.g., a log file, a plot) for a run.

        Args:
            run_id: The ID of the run.
            content: The content of the artifact (string or bytes).
            artifact_name: The filename for the artifact (e.g., "run.log" or "energy_plot.png").
        """
        run_path = self.get_run_path(run_id)
        artifacts_path = run_path / "artifacts"
        artifacts_path.mkdir(exist_ok=True)

        file_path = artifacts_path / artifact_name
        if isinstance(content, str):
            file_path.write_text(content)
        else:
            file_path.write_bytes(content)

    def get_constellation_path(self) -> Path:
        """Gets the path for storing the constellation memory."""
        path = self.base_path / "memory"
        path.mkdir(exist_ok=True)
        return path / "constellation_graph.json"

    def save_constellation(self, constellation: ConstellationMemory):
        """Saves the constellation memory graph to a file."""
        file_path = self.get_constellation_path()
        graph_data = nx.node_link_data(constellation.graph)

        with file_path.open('w') as f:
            json.dump(graph_data, f, cls=NumpyJSONEncoder, indent=4)

    def load_constellation(self, constellation: ConstellationMemory):
        """Loads the constellation memory graph from a file."""
        file_path = self.get_constellation_path()
        if not file_path.exists():
            return  # No saved constellation to load

        with file_path.open('r') as f:
            graph_data = json.load(f)

        # Manually parse datetime strings back to datetime objects
        for node in graph_data.get('nodes', []):
            if 'timestamp' in node and isinstance(node['timestamp'], str):
                node['timestamp'] = datetime.fromisoformat(node['timestamp'])

        for link in graph_data.get('links', []):
            if 'timestamp' in link and isinstance(link['timestamp'], str):
                link['timestamp'] = datetime.fromisoformat(link['timestamp'])

        constellation.graph = nx.node_link_graph(graph_data)


# Example Usage
if __name__ == '__main__':
    from uuid import uuid4
    from datetime import datetime
    from core.types import SoftwareState, EnergyComponents, QuantumState

    # Setup persistence manager in a temporary directory
    temp_storage = Path("./temp_persistence_storage")
    manager = PersistenceManager(temp_storage)

    run_id = uuid4()
    print(f"--- Managing run: {run_id} ---")

    # Create a state to save as a snapshot
    qc_state = QCState(
        id=uuid4(), timestamp=datetime.utcnow(),
        software_state=SoftwareState(component_versions={"a":"1"}, config_hashes={"b":"2"}, status="nominal"),
        energy=10.5, energy_components=EnergyComponents(static=5.0, dynamic=5.5, interaction=0.0),
        lyapunov_potential=0.5, contraction_factor=0.8, optimization_phase="exploitation",
        quantum_state=QuantumState(state_vector=[1.0, 0.0], density_matrix=None)
    )

    # Save a snapshot
    manager.save_snapshot(run_id, qc_state, "initial_state")
    print("\nSaved 'initial_state' snapshot.")

    # Load the snapshot
    loaded_snapshot = manager.load_snapshot(run_id, "initial_state")
    if loaded_snapshot:
        print("Loaded snapshot successfully.")
        assert loaded_snapshot.id == qc_state.id

    # Save a generic artifact
    log_content = "Run started.\nIteration 100: Energy = 12.3\nRun finished."
    manager.save_artifact(run_id, log_content, "run.log")
    print("\nSaved 'run.log' artifact.")

    # Save a final run record
    run_record = RunRecord(
        run_id=run_id, start_time=datetime.utcnow(), end_time=datetime.utcnow(),
        status="completed", initial_state=qc_state, final_state=loaded_snapshot
    )
    manager.save_run_record(run_record)
    print("\nSaved final run record.")

    # Load the run record
    loaded_record = manager.load_run_record(run_id)
    if loaded_record:
        print("Loaded run record successfully.")
        assert loaded_record.run_id == run_id

    print(f"\nCheck the contents of the directory: {temp_storage.resolve()}")

    # To see the created structure, you could manually inspect the directory.
    # The structure should be:
    # temp_persistence_storage/
    #   ├── run_records/
    #   │   └── {run_id}.json
    #   └── runs/
    #       └── {run_id}/
    #           ├── snapshots/
    #           │   └── initial_state.json
    #           └── artifacts/
    #               └── run.log

    # Clean up
    import shutil
    shutil.rmtree(temp_storage)
    print(f"\nCleaned up temporary directory: {temp_storage}")
