import pytest
from datetime import datetime, timedelta
from core.types import (
    QCState,
    SoftwareState,
    EnergyBreakdown,
    QuantumState,
    RunRecord,
    LyapunovMetrics,
)
from core.validators import (
    validate_qc_state_consistency,
    validate_run_record,
    validate_software_state,
    ValidationError,
)

# Helper to create a default valid QCState
def create_valid_qc_state(phase="initialization", lyapunov=0.5, has_quantum_state=True):
    software_state = SoftwareState(
        component_versions={"comp": "1.0"}, config_hashes={"conf": "abc"}
    )
    energy_breakdown = EnergyBreakdown(total=2.0, complexity=1.0, coupling=0.5, constraint=0.5, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=lyapunov, energy=energy_breakdown.total, test_penalty=0.0, obligation_penalty=0.0)
    quantum_state = None
    if has_quantum_state:
        quantum_state = QuantumState(state_vector=[1.0, 0.0])

    return QCState(
        software_state=software_state,
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
        contraction_factor=0.5,
        phase=phase,
        quantum_state=quantum_state,
    )

def test_validate_qc_state_consistency_valid():
    """Tests that a consistent QCState passes validation."""
    state = create_valid_qc_state(phase="exploitation", lyapunov=0.5)
    validate_qc_state_consistency(state)  # Should not raise

def test_validate_qc_state_consistency_high_lyapunov():
    """Tests for high Lyapunov potential during exploitation phase."""
    state = create_valid_qc_state(phase="exploitation", lyapunov=1.5)
    with pytest.raises(ValidationError, match="High Lyapunov potential"):
        validate_qc_state_consistency(state)

def test_validate_qc_state_consistency_missing_quantum_state():
    """Tests for missing quantum state after initialization."""
    state = create_valid_qc_state(phase="convergence", has_quantum_state=False)
    with pytest.raises(ValidationError, match="Quantum state must be present"):
        validate_qc_state_consistency(state)

def test_validate_qc_state_unnormalized_vector():
    """Tests for non-normalized quantum state vector."""
    state = create_valid_qc_state()
    state.quantum_state.state_vector = [2.0, 0.0]
    with pytest.raises(ValidationError, match="Quantum state vector is not normalized"):
        validate_qc_state_consistency(state)

def test_validate_run_record_valid():
    """Tests a valid RunRecord."""
    initial_state = create_valid_qc_state()
    # Create a valid final_state with decreased energy
    final_state = initial_state.model_copy(update={
        'energy_breakdown': EnergyBreakdown(total=1.0, complexity=0.5, coupling=0.25, constraint=0.25, debt=0.0),
        'timestamp': initial_state.timestamp + timedelta(seconds=1)
    })

    record = RunRecord(
        start_time=datetime.utcnow() - timedelta(minutes=1),
        end_time=datetime.utcnow(),
        status="completed",
        initial_state=initial_state,
        final_state=final_state,
    )
    validate_run_record(record) # Should not raise

def test_validate_run_record_high_final_energy():
    """Tests for significantly higher final energy in a completed run."""
    initial_state = create_valid_qc_state()
    # Create a valid final_state with increased energy
    final_state = initial_state.model_copy(update={
        'energy_breakdown': EnergyBreakdown(total=3.0, complexity=1.0, coupling=1.0, constraint=1.0, debt=0.0),
    })

    record = RunRecord(
        start_time=datetime.utcnow() - timedelta(minutes=1),
        end_time=datetime.utcnow(),
        status="completed",
        initial_state=initial_state,
        final_state=final_state,
    )
    with pytest.raises(ValidationError, match="Final energy in completed run is significantly higher"):
        validate_run_record(record)

def test_validate_run_record_invalid_timestamp_order():
    """Tests for final state timestamp being before initial state."""
    initial_state = create_valid_qc_state()
    final_state = initial_state.model_copy()
    final_state.timestamp = initial_state.timestamp - timedelta(seconds=1)

    record = RunRecord(
        start_time=datetime.utcnow() - timedelta(minutes=1),
        end_time=datetime.utcnow(),
        status="completed",
        initial_state=initial_state,
        final_state=final_state,
    )
    with pytest.raises(ValidationError, match="Final state timestamp cannot be before initial state timestamp"):
        validate_run_record(record)

def test_validate_software_state_valid():
    """Tests a valid SoftwareState."""
    state = SoftwareState(
        component_versions={"comp1": "1.0.0"},
        config_hashes={"conf1": "hash123"},
    )
    validate_software_state(state) # Should not raise

@pytest.mark.parametrize("versions,hashes,match_str", [
    ({"comp": ""}, {"conf": "h"}, "Component versions contain empty names or values"),
    ({"": "1.0"}, {"conf": "h"}, "Component versions contain empty names or values"),
    ({"comp": "1.0"}, {"conf": ""}, "Config hashes contain empty names or values"),
    ({"comp": "1.0"}, {"": "h"}, "Config hashes contain empty names or values"),
])
def test_validate_software_state_invalid(versions, hashes, match_str):
    """Tests for invalid SoftwareState with empty values or keys."""
    state = SoftwareState(component_versions=versions, config_hashes=hashes)
    with pytest.raises(ValidationError, match=match_str):
        validate_software_state(state)
