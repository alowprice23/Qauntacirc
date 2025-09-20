import pytest
from unittest.mock import patch, MagicMock
from agents.fluctua_test.agent import FluctuaTestAgent
from core.types import SystemState, EnergyBreakdown, LyapunovMetrics, SoftwareState
from core.chaos_types import ChaosPlanResult, ChaosScenario

@pytest.fixture
def fluctuatest_agent():
    """Fixture for a FluctuaTestAgent instance, with scenarios mocked."""
    agent = FluctuaTestAgent()
    # Directly set the scenarios on the instance to bypass import/patching issues
    mock_scenario = ChaosScenario(
        name="test_scenario",
        description="A mock scenario for testing.",
        target_components=["component_a"],
        fault_injection=lambda: "Injected fault!",
        expected_behavior="System should recover within 30 seconds.",
        recovery_criteria={"metric": "latency", "threshold": 100},
        blast_radius=0.5,
        duration_seconds=60
    )
    agent.chaos_scenarios = [mock_scenario]
    return agent

@pytest.fixture
def initial_state():
    """Fixture for a default SystemState."""
    return SystemState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0),
        metadata={"risk_budget": 1.0} # Set to 1.0 to ensure scenario is selected
    )

def test_apply_physics_principle_proposes_plan(fluctuatest_agent, initial_state):
    """
    Tests that apply_physics_principle returns a valid chaos testing plan.
    """
    # Act
    result = fluctuatest_agent.apply_physics_principle(initial_state)

    # Assert
    assert isinstance(result, ChaosPlanResult)
    assert result.success is True
    assert result.agent_name == "fluctua_test"
    assert result.physics_principle == "Fluctuation-Dissipation Theorem"

    # Check that a plan was generated
    assert result.chaos_plan is not None
    # With a risk budget of 1.0 and 1 mock scenario, we expect 1 to be selected
    assert len(result.chaos_plan.scenarios) == 1
    assert result.chaos_plan.scenarios[0].name == "test_scenario"
    assert len(result.chaos_plan.execution_order) == len(result.chaos_plan.scenarios)
    assert result.chaos_plan.monitoring_setup is not None
    assert result.chaos_plan.recovery_procedures is not None

def test_apply_physics_principle_no_scenarios_selected(fluctuatest_agent, initial_state):
    """
    Tests that the agent handles the case where no scenarios are selected,
    e.g., due to a zero risk budget.
    """
    # Arrange
    initial_state.metadata["risk_budget"] = 0.0

    # Act
    result = fluctuatest_agent.apply_physics_principle(initial_state)

    # Assert
    assert isinstance(result, ChaosPlanResult)
    assert result.success is True
    assert result.chaos_plan is not None
    assert len(result.chaos_plan.scenarios) == 0
    assert len(result.chaos_plan.execution_order) == 0
