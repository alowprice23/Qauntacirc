import pytest
import json
from uuid import uuid4
from datetime import datetime
from core.run_ledger import RunLedger
from core.data_models import RunRecord, QCState, SoftwareState, EnergyComponents, EnergyBreakdown, LyapunovMetrics

@pytest.fixture
def dummy_run_record():
    """Creates a valid RunRecord for testing."""
    initial_state = QCState(
        software_state=SoftwareState(component_versions={}, config_hashes={}),
        energy_breakdown=EnergyBreakdown(total=10.0, complexity=5.0, coupling=5.0, constraint=0.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=0.5, energy=10.0, test_penalty=0.0, obligation_penalty=0.0),
        contraction_factor=0.8,
    )
    final_state = initial_state.model_copy(deep=True)
    final_state.energy_breakdown.total = 8.0
    final_state.energy_breakdown.complexity = 4.0
    final_state.energy_breakdown.coupling = 4.0
    final_state.lyapunov_metrics.energy = 8.0

    return RunRecord(
        run_id=uuid4(),
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow(),
        status="completed",
        initial_state=initial_state,
        final_state=final_state,
    )

def test_ledger_init(tmp_path):
    """Tests that the ledger creates its storage directory."""
    ledger_path = tmp_path / "test_ledger"
    assert not ledger_path.exists()
    ledger = RunLedger(ledger_path)
    assert ledger.storage_path.exists()

def test_add_and_get_record(tmp_path, dummy_run_record):
    """Tests adding a record and retrieving it."""
    ledger = RunLedger(tmp_path)

    # Add record
    ledger.add_record(dummy_run_record)

    # Check that file was created
    expected_file = tmp_path / f"{dummy_run_record.run_id}.json"
    assert expected_file.exists()

    # Retrieve record
    retrieved_record = ledger.get_record(dummy_run_record.run_id)
    assert retrieved_record is not None
    assert retrieved_record.run_id == dummy_run_record.run_id
    assert retrieved_record.status == "completed"
    assert retrieved_record.final_state.energy_breakdown.total == 8.0

def test_get_nonexistent_record(tmp_path):
    """Tests that getting a non-existent record returns None."""
    ledger = RunLedger(tmp_path)
    assert ledger.get_record(uuid4()) is None

def test_list_records(tmp_path, dummy_run_record):
    """Tests listing record IDs."""
    ledger = RunLedger(tmp_path)

    record2 = dummy_run_record.model_copy(update={'run_id': uuid4()})

    ledger.add_record(dummy_run_record)
    ledger.add_record(record2)

    record_ids = ledger.list_records()
    assert len(record_ids) == 2
    assert dummy_run_record.run_id in record_ids
    assert record2.run_id in record_ids

def test_list_records_ignores_invalid_files(tmp_path, dummy_run_record):
    """Tests that invalid files in the storage path are ignored."""
    ledger = RunLedger(tmp_path)
    ledger.add_record(dummy_run_record)

    # Create invalid files
    (tmp_path / "not-a-uuid.json").touch()
    (tmp_path / "another_file.txt").touch()

    record_ids = ledger.list_records()
    assert len(record_ids) == 1
    assert dummy_run_record.run_id in record_ids

def test_get_all_records(tmp_path, dummy_run_record):
    """Tests retrieving all records."""
    ledger = RunLedger(tmp_path)

    record2 = dummy_run_record.model_copy(update={'run_id': uuid4()})

    ledger.add_record(dummy_run_record)
    ledger.add_record(record2)

    all_records = ledger.get_all_records()
    assert len(all_records) == 2

    retrieved_ids = {r.run_id for r in all_records}
    assert dummy_run_record.run_id in retrieved_ids
    assert record2.run_id in retrieved_ids

def test_record_serialization_and_deserialization(tmp_path, dummy_run_record):
    """Verifies the content of the serialized JSON file."""
    ledger = RunLedger(tmp_path)
    ledger.add_record(dummy_run_record)

    file_path = tmp_path / f"{dummy_run_record.run_id}.json"
    with open(file_path, 'r') as f:
        data = json.load(f)

    assert data["run_id"] == str(dummy_run_record.run_id)
    assert data["status"] == "completed"
    assert data["initial_state"]["energy_breakdown"]["total"] == 10.0
    assert "start_time" in data

    # Test deserialization
    retrieved_record = RunRecord.model_validate(data)
    assert retrieved_record.run_id == dummy_run_record.run_id
