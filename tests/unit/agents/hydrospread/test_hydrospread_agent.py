import pytest
from agents.hydro_spread.agent import HydroSpreadAgent
from core.types import SystemState, GrowthParameters, GrowthPrediction, EnergyBreakdown, LyapunovMetrics, SoftwareState

@pytest.fixture
def hydrospread_agent():
    """Fixture for a HydroSpreadAgent instance."""
    return HydroSpreadAgent()

@pytest.fixture
def system_state_for_growth():
    """Fixture for a SystemState with data for growth prediction."""
    growth_params = {
        "density": 1.2,
        "gravity": 9.8,
        "time_horizons": [1, 10, 100]
    }

    state = SystemState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0),
        module_count=10,
        team_size=5,
        total_complexity=50.0,
        coupling_density=0.2,
        current_volume=100.0,
        metadata={
            "hydro_spread_input": {
                "growth_parameters": growth_params
            }
        }
    )
    return state

def test_apply_physics_principle_success(hydrospread_agent, system_state_for_growth):
    """
    Tests that apply_physics_principle correctly predicts system growth.
    """
    # Act
    result = hydrospread_agent.apply_physics_principle(system_state_for_growth)

    # Assert
    assert isinstance(result, GrowthPrediction)
    assert result.success is True
    assert result.agent_name == "hydro_spread"
    assert result.physics_principle == "Viscous Spreading"

    # Check that predictions were generated for all time horizons
    assert len(result.predictions) == 3
    assert result.predictions[0].time == 1
    assert result.predictions[1].time == 10
    assert result.predictions[2].time == 100

    # Check that viscosity and spreading coefficient were calculated
    assert result.viscosity > 0
    assert result.spreading_coefficient > 0

    # Check that growth is predicted
    assert result.predictions[0].predicted_radius < result.predictions[-1].predicted_radius

def test_apply_physics_principle_missing_metadata(hydrospread_agent):
    """
    Tests that the agent raises a ValueError if growth_parameters are missing.
    """
    state = SystemState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0),
        metadata={} # Missing hydro_spread_input
    )

    with pytest.raises(ValueError, match="HydroSpreadAgent requires 'growth_parameters' in metadata."):
        hydrospread_agent.apply_physics_principle(state)
