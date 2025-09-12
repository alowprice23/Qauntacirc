import pytest
from core.types import SoftwareState, QCState, EnergyComponents, EnergyBreakdown, LyapunovMetrics
from core.edit_distance import software_state_edit_distance, qcstate_edit_distance

@pytest.fixture
def base_state():
    """A base SoftwareState for comparison."""
    return SoftwareState(
        component_versions={"compA": "1.0", "compB": "2.0"},
        config_hashes={"conf1": "hashA", "conf2": "hashB"},
        status="nominal"
    )

def test_distance_identical_states(base_state):
    """Distance between identical states should be 0."""
    state_b = base_state.model_copy(deep=True)
    assert software_state_edit_distance(base_state, state_b) == 0

def test_distance_one_version_change(base_state):
    """Distance with a single version change."""
    state_b = base_state.model_copy(deep=True)
    state_b.component_versions["compA"] = "1.1"
    assert software_state_edit_distance(base_state, state_b) == 1

def test_distance_one_hash_change(base_state):
    """Distance with a single hash change."""
    state_b = base_state.model_copy(deep=True)
    state_b.config_hashes["conf1"] = "hashC"
    assert software_state_edit_distance(base_state, state_b) == 1

def test_distance_status_change(base_state):
    """Distance with a status change."""
    state_b = base_state.model_copy(deep=True)
    state_b.status = "degraded"
    assert software_state_edit_distance(base_state, state_b) == 1

def test_distance_multiple_changes(base_state):
    """Distance with multiple changes across all fields."""
    state_b = base_state.model_copy(deep=True)
    state_b.component_versions["compA"] = "1.1"
    state_b.config_hashes["conf2"] = "hashD"
    state_b.status = "error"
    assert software_state_edit_distance(base_state, state_b) == 3

def test_distance_component_added(base_state):
    """Distance when a component is added."""
    state_b = base_state.model_copy(deep=True)
    state_b.component_versions["compC"] = "3.0"
    assert software_state_edit_distance(base_state, state_b) == 1

def test_distance_component_removed(base_state):
    """Distance when a component is removed."""
    state_b = base_state.model_copy(deep=True)
    del state_b.component_versions["compA"]
    assert software_state_edit_distance(base_state, state_b) == 1

def test_distance_completely_different():
    """Distance between two completely different states."""
    state_a = SoftwareState(
        component_versions={"a": "1"}, config_hashes={"b": "2"}, status="x"
    )
    state_b = SoftwareState(
        component_versions={"c": "3"}, config_hashes={"d": "4"}, status="y"
    )
    # a vs c -> 2 changes
    # b vs d -> 2 changes
    # x vs y -> 1 change
    assert software_state_edit_distance(state_a, state_b) == 5

def test_distance_is_symmetric(base_state):
    """Tests that the distance function is symmetric."""
    state_b = base_state.model_copy(deep=True)
    state_b.component_versions["compA"] = "1.1"
    state_b.config_hashes["conf1"] = "hashC"

    dist_ab = software_state_edit_distance(base_state, state_b)
    dist_ba = software_state_edit_distance(state_b, base_state)
    assert dist_ab == dist_ba

def test_triangle_inequality():
    """Tests that the distance function satisfies the triangle inequality."""
    state_a = SoftwareState(
        component_versions={"a": "1"}, config_hashes={}, status="x"
    )
    state_b = SoftwareState(
        component_versions={"a": "2"}, config_hashes={}, status="y"
    )
    state_c = SoftwareState(
        component_versions={"a": "3"}, config_hashes={}, status="z"
    )

    dist_ac = software_state_edit_distance(state_a, state_c) # a: 1->3 (1), status: x->z (1) => 2
    dist_ab = software_state_edit_distance(state_a, state_b) # a: 1->2 (1), status: x->y (1) => 2
    dist_bc = software_state_edit_distance(state_b, state_c) # a: 2->3 (1), status: y->z (1) => 2

    assert dist_ac <= dist_ab + dist_bc

def test_qcstate_edit_distance_wrapper(base_state):
    """Tests the QCState wrapper function."""
    qc_state_a = QCState(
        software_state=base_state,
        energy_breakdown=EnergyBreakdown(total=0, complexity=0, coupling=0, constraint=0, debt=0),
        lyapunov_metrics=LyapunovMetrics(phi=0, energy=0, test_penalty=0, obligation_penalty=0),
        contraction_factor=0.5
    )

    state_b = base_state.model_copy(deep=True)
    state_b.status = "degraded"
    qc_state_b = QCState(
        software_state=state_b,
        energy_breakdown=EnergyBreakdown(total=0, complexity=0, coupling=0, constraint=0, debt=0),
        lyapunov_metrics=LyapunovMetrics(phi=0, energy=0, test_penalty=0, obligation_penalty=0),
        contraction_factor=0.5
    )

    assert qcstate_edit_distance(qc_state_a, qc_state_b) == 1
    assert qcstate_edit_distance(qc_state_a, qc_state_b) == software_state_edit_distance(base_state, state_b)
