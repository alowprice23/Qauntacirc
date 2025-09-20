import pytest
from agents.bose_boost.agent import BoseBoostAgent
from core.types import SystemState, WorkloadDistribution, ResourceAllocation, EnergyBreakdown, LyapunovMetrics, SoftwareState

@pytest.fixture
def bose_agent():
    """Fixture for a BoseBoostAgent instance."""
    return BoseBoostAgent()

@pytest.fixture
def system_state_with_workload():
    """Fixture for a SystemState with a sample workload for BoseBoost."""
    workload_data = {
        "tasks": {
            "api_requests": {"complexity": 2.5, "priority": 1},
            "data_processing": {"complexity": 8.0, "priority": 2},
            "background_jobs": {"complexity": 1.5, "priority": 3}
        },
        "total_resources": 10.0,
        "max_replicas_per_task": 5
    }

    state = SystemState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0),
        metadata={
            "bose_boost_input": {
                "workload": workload_data,
                "temperature": 1.0
            }
        }
    )
    return state

def test_apply_physics_principle_success(bose_agent, system_state_with_workload):
    """
    Tests that apply_physics_principle correctly allocates resources
    based on the provided workload in the system state.
    """
    # Act
    result = bose_agent.apply_physics_principle(system_state_with_workload)

    # Assert
    assert isinstance(result, ResourceAllocation)
    assert result.success is True
    assert result.agent_name == "bose_boost"
    assert result.physics_principle == "Bose-Einstein Statistics"

    # Check that allocations were created for all tasks
    assert "api_requests" in result.allocations
    assert "data_processing" in result.allocations
    assert "background_jobs" in result.allocations

    # Check that replicas are allocated. The exact number depends on the solver,
    # but we expect some allocation.
    total_replicas = sum(alloc["replicas"] for alloc in result.allocations.values())
    assert total_replicas > 0
    assert total_replicas <= 10.0 # Should not exceed total resources

    # Check that higher energy (complexity) tasks get fewer resources
    api_replicas = result.allocations["api_requests"]["replicas"]
    data_replicas = result.allocations["data_processing"]["replicas"]
    background_replicas = result.allocations["background_jobs"]["replicas"]

    assert data_replicas <= api_replicas
    assert data_replicas <= background_replicas

def test_apply_physics_principle_no_workload(bose_agent):
    """
    Tests that the agent raises a ValueError if the workload is missing.
    """
    state = SystemState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0),
        metadata={} # Missing bose_boost_input
    )

    with pytest.raises(ValueError, match="BoseBoostAgent requires a 'workload' in metadata."):
        bose_agent.apply_physics_principle(state)
