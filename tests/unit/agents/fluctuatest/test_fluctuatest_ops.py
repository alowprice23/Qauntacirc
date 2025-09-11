import pytest
from agents.fluctuatest.ops import parse_chaos_experiment_proposal, ChaosSimulator, ChaosExperimentError
from core.types import QCState, SoftwareState, EnergyComponents

def test_parse_chaos_experiment_proposal_success():
    llm_output = '{"hypothesis": "h", "experiment_type": "e", "magnitude": "m", "duration_seconds": 1}'
    proposal = parse_chaos_experiment_proposal(llm_output)
    assert "hypothesis" in proposal

def test_parse_chaos_experiment_proposal_invalid_json():
    with pytest.raises(ChaosExperimentError, match="Failed to decode"):
        parse_chaos_experiment_proposal("not json")

def test_parse_chaos_experiment_proposal_missing_keys():
    with pytest.raises(ChaosExperimentError, match="missing required keys"):
        parse_chaos_experiment_proposal('{"hypothesis": ""}')

@pytest.fixture
def initial_state():
    software_state = SoftwareState(component_versions={}, config_hashes={}, status="initial")
    energy_components = EnergyComponents(static=100.0, dynamic=50.0, interaction=20.0)
    return QCState(
        software_state=software_state,
        energy=energy_components.total,
        energy_components=energy_components,
        lyapunov_potential=170.0,
        contraction_factor=1.0,
    )

def test_chaos_simulator(initial_state):
    simulator = ChaosSimulator()
    experiment = {"experiment_type": "latency_injection", "magnitude": 10.0}
    new_state = simulator.run_experiment(initial_state, experiment)

    assert new_state.energy > initial_state.energy
    assert new_state.energy_components.dynamic == initial_state.energy_components.dynamic + 10.0
