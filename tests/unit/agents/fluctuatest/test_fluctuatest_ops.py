import pytest
from agents.fluctuatest.ops import parse_chaos_experiment_proposal, ChaosSimulator, ChaosExperimentError
from core.types import SystemState, SoftwareState, EnergyBreakdown, LyapunovMetrics

def test_parse_chaos_experiment_proposal_success():
    llm_output = '{"hypothesis": "h", "experiment_type": "e", "magnitude": 10.0, "duration_seconds": 1}'
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
    return SystemState(
        software_state=SoftwareState(status="initial"),
        energy_breakdown=EnergyBreakdown(
            total=170.0,
            complexity=100.0,
            coupling=50.0,
            constraint=20.0,
            debt=0.0,
        ),
        lyapunov_metrics=LyapunovMetrics(
            phi=170.0,
            energy=170.0,
            test_penalty=0.0,
            obligation_penalty=0.0,
        ),
        contraction_factor=1.0,
    )

def test_chaos_simulator_latency_injection(initial_state):
    """Tests that a latency injection experiment correctly increases debt and total energy."""
    simulator = ChaosSimulator()
    experiment = {"experiment_type": "latency_injection", "magnitude": 10.0}

    initial_debt = initial_state.energy_breakdown.debt
    initial_energy = initial_state.lyapunov_metrics.energy

    new_state = simulator.run_experiment(initial_state, experiment)

    assert new_state.lyapunov_metrics.energy > initial_energy
    assert new_state.energy_breakdown.debt == initial_debt + 10.0
