import pytest
import numpy as np
from core.state_space import StateSpace
from core.types import QCState, QuantumState, SoftwareState, EnergyComponents

# Helper to create a dummy QCState for testing
def create_dummy_qc_state(vector):
    if vector:
        # Ensure elements are native python types for Pydantic validation
        vector = [complex(v) for v in vector]
    return QCState(
        software_state=SoftwareState(component_versions={}, config_hashes={}),
        energy=0,
        energy_components=EnergyComponents(static=0, dynamic=0, interaction=0),
        lyapunov_potential=0,
        contraction_factor=0.5,
        quantum_state=QuantumState(state_vector=vector) if vector else None
    )

def test_state_space_init():
    """Tests StateSpace initialization."""
    space = StateSpace(dimension=4)
    assert space.get_dimension() == 4

    with pytest.raises(ValueError, match="State space dimension must be positive"):
        StateSpace(dimension=0)
    with pytest.raises(ValueError, match="State space dimension must be positive"):
        StateSpace(dimension=-1)

def test_is_valid_state():
    """Tests the is_valid_state method."""
    space = StateSpace(dimension=2)

    # Valid state
    valid_state = create_dummy_qc_state([1.0, 0.0])
    assert space.is_valid_state(valid_state)

    # State with no quantum component
    no_quantum_state = create_dummy_qc_state(None)
    assert not space.is_valid_state(no_quantum_state)

    # State with wrong dimension
    wrong_dim_state = create_dummy_qc_state([1.0, 0.0, 0.0])
    assert not space.is_valid_state(wrong_dim_state)

    # State that is not normalized
    unnormalized_state = create_dummy_qc_state([1.0, 1.0])
    assert not space.is_valid_state(unnormalized_state)

def test_get_basis_vector():
    """Tests the get_basis_vector method."""
    space = StateSpace(dimension=4)
    vec0 = space.get_basis_vector(0)
    vec3 = space.get_basis_vector(3)

    assert vec0 == [1.0, 0.0, 0.0, 0.0]
    assert vec3 == [0.0, 0.0, 0.0, 1.0]

    with pytest.raises(IndexError, match="Basis vector index is out of bounds"):
        space.get_basis_vector(4)
    with pytest.raises(IndexError, match="Basis vector index is out of bounds"):
        space.get_basis_vector(-1)

def test_get_random_state_vector():
    """Tests the get_random_state_vector method."""
    space = StateSpace(dimension=8)
    random_vec = space.get_random_state_vector()

    assert len(random_vec) == 8
    assert np.isclose(np.linalg.norm(random_vec), 1.0)

def test_compute_distance_invalid_state():
    """Tests distance computation with an invalid state."""
    space = StateSpace(dimension=2)
    state_a = create_dummy_qc_state([1.0, 0.0])
    state_b = create_dummy_qc_state([1.0, 1.0]) # Not normalized

    with pytest.raises(ValueError, match="One or both states are not valid"):
        space.compute_distance(state_a, state_b)

def test_compute_distance_metrics():
    """Tests the different distance metrics."""
    space = StateSpace(dimension=2)
    state_a = create_dummy_qc_state([1.0, 0.0]) # |0>
    state_b = create_dummy_qc_state([0.0, 1.0]) # |1>
    state_c = create_dummy_qc_state([1/np.sqrt(2), 1/np.sqrt(2)]) # |+>

    # Fidelity distance
    # Fidelity |<0|1>|^2 = 0, distance = sqrt(1-0) = 1
    dist_ab_fid = space.compute_distance(state_a, state_b, metric='fidelity')
    assert np.isclose(dist_ab_fid, 1.0)

    # Fidelity |<0|+>|^2 = 0.5, distance = sqrt(1-0.5) = sqrt(0.5)
    dist_ac_fid = space.compute_distance(state_a, state_c, metric='fidelity')
    assert np.isclose(dist_ac_fid, np.sqrt(0.5))

    # Euclidean distance
    dist_ab_euc = space.compute_distance(state_a, state_b, metric='euclidean')
    assert np.isclose(dist_ab_euc, np.sqrt(2))

    dist_ac_euc = space.compute_distance(state_a, state_c, metric='euclidean')
    expected_dist = np.linalg.norm(np.array([1.0, 0.0]) - np.array([1/np.sqrt(2), 1/np.sqrt(2)]))
    assert np.isclose(dist_ac_euc, expected_dist)

def test_compute_distance_unsupported_metric():
    """Tests using an unsupported distance metric."""
    space = StateSpace(dimension=2)
    state_a = create_dummy_qc_state([1.0, 0.0])
    state_b = create_dummy_qc_state([0.0, 1.0])

    with pytest.raises(ValueError, match="Unsupported distance metric"):
        space.compute_distance(state_a, state_b, metric='manhattan')
