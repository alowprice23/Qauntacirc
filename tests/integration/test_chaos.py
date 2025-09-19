import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from core.orchestrator import Orchestrator
from agents.fluctua_test.agent import FluctuaTestAgent
from monitoring.resilience import ResilienceMonitor
from core.types import SystemState, EnergyBreakdown, LyapunovMetrics, SoftwareState
from core.chaos_types import ChaosPlanResult, ChaosTestingPlan, ResilienceReport

@pytest.fixture
def mock_system_state():
    """Fixture for a mock SystemState."""
    return SystemState(
        software_state=SoftwareState(),
        modules=[],
        requirements=[],
        total_complexity=100.0,
        energy_breakdown=EnergyBreakdown(total=1000.0, complexity=500.0, coupling=300.0, constraint=100.0, debt=100.0),
        lyapunov_metrics=LyapunovMetrics(phi=1.0, energy=1000.0, test_penalty=0.0, obligation_penalty=0.0),
        metadata={"risk_budget": 0.6}
    )

@pytest.fixture
def fluctua_test_agent():
    """Fixture for the FluctuaTestAgent."""
    return FluctuaTestAgent()

@pytest.fixture
def mock_orchestrator(fluctua_test_agent):
    """Fixture for a mock Orchestrator."""
    # Mock dependencies for the orchestrator
    energy_calculator = MagicMock()
    lyapunov_monitor = MagicMock()
    closure_validator = MagicMock()
    comm_protocol = MagicMock()

    # Configure mocks to return valid objects
    energy_calculator.compute_total_energy.return_value = EnergyBreakdown(total=1000.0, complexity=500.0, coupling=300.0, constraint=100.0, debt=100.0)
    lyapunov_monitor.compute.return_value = LyapunovMetrics(phi=1.0, energy=1000.0, test_penalty=0.0, obligation_penalty=0.0)

    orchestrator = Orchestrator(
        agents=[fluctua_test_agent],
        energy_calculator=energy_calculator,
        lyapunov_monitor=lyapunov_monitor,
        closure_validator=closure_validator,
        communication_protocol=comm_protocol,
    )
    return orchestrator

@pytest.mark.asyncio
async def test_fluctua_test_agent_proposes_plan(fluctua_test_agent, mock_system_state):
    """
    Test that the FluctuaTestAgent can generate a chaos testing plan.
    """
    result = fluctua_test_agent.apply_physics_principle(mock_system_state)

    assert isinstance(result, ChaosPlanResult)
    assert isinstance(result.chaos_plan, ChaosTestingPlan)
    # Based on risk budget of 0.6, we expect 3 scenarios (0.6 * 5 scenarios)
    assert len(result.chaos_plan.scenarios) == 3

@pytest.mark.asyncio
async def test_orchestrator_executes_chaos_plan(mock_orchestrator, mock_system_state):
    """
    Test that the Orchestrator can receive a chaos plan and execute it.
    """
    # We mock the _execute_chaos_plan to avoid running the actual async logic,
    # and to verify it's called with the correct plan.
    mock_orchestrator._execute_chaos_plan = AsyncMock(
        return_value=[
            ResilienceReport(
                scenario_name="test_scenario",
                baseline_metrics={}, chaos_metrics={}, recovery_metrics={},
                resilience_score=0.8, recovery_time=10.0, sla_violations=0,
                data_consistency_maintained=True, recommendations=[]
            )
        ]
    )

    # The agent selection is round-robin, so it will select our agent.
    evolution = await mock_orchestrator.evolve_system(mock_system_state)

    # Verify that the execution method was called.
    mock_orchestrator._execute_chaos_plan.assert_awaited_once()

    # Check that the final state has the chaos reports in its metadata.
    final_state = evolution.final_state
    assert "chaos_reports" in final_state.metadata
    assert len(final_state.metadata["chaos_reports"]) == 1
    assert final_state.metadata["chaos_reports"][0]["scenario_name"] == "test_scenario"

@pytest.mark.asyncio
async def test_resilience_monitor_generates_report():
    """
    Test that the ResilienceMonitor can monitor a scenario and generate a report.
    """
    monitor = ResilienceMonitor()

    # Create a mock scenario
    mock_fault_injection = AsyncMock(return_value={"status": "success"})
    mock_scenario = MagicMock()
    mock_scenario.name = "mock_scenario"
    mock_scenario.target_components = ["mock_component"]
    mock_scenario.duration_seconds = 1
    mock_scenario.fault_injection = mock_fault_injection
    mock_scenario.recovery_criteria = {"max_recovery_time": 5}

    report = await monitor.monitor_chaos_scenario(mock_scenario, baseline_duration=1)

    assert isinstance(report, ResilienceReport)
    assert report.scenario_name == "mock_scenario"
    assert "latency_ms" in report.baseline_metrics
    assert report.resilience_score is not None
    mock_fault_injection.assert_awaited_once_with(["mock_component"], 1)
