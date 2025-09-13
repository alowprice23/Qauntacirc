import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.fluctua_test.agent import FluctuaTestAgent
from core.data_models import SystemState, AgentTask, EnergyBreakdown, LyapunovMetrics, Status, SoftwareState
from datetime import datetime

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {"content": '{"hypothesis": "h", "experiment_type": "latency_injection", "magnitude": 100, "duration_seconds": 30}'}
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"stability_threshold": 50.0}
    return calculator

@pytest.fixture
def fluctuatest_agent(mock_llm_client, mock_energy_calculator):
    return FluctuaTestAgent(
        state_space=MagicMock(),
        energy_calculator=mock_energy_calculator,
        metrics_logger=MagicMock(),
        policy_engine=MagicMock(),
        agent_memory=MagicMock(),
        llm_client=mock_llm_client
    )

@pytest.fixture
def initial_state():
    energy_breakdown = EnergyBreakdown(total=170.0, complexity=100.0, coupling=50.0, constraint=20.0, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=170.0, energy=170.0, test_penalty=0.0, obligation_penalty=0.0)
    return SystemState(
        software_state=SoftwareState(),
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
    )

@pytest.mark.asyncio
async def test_analyze_state_success(fluctuatest_agent, initial_state):
    proposal = fluctuatest_agent.analyze_state(initial_state)
    assert proposal.status == Status.SUCCESS
    assert "chaos_test_result" in proposal.payload
    result = proposal.payload["chaos_test_result"]
    assert result["scenarios_generated"] > 0

def test_execute_stable(fluctuatest_agent, initial_state):
    proposal = AgentTask(
        agent_name="fluctuatest",
        task_type="chaos_test",
        payload={"chaos_test_result": {"resilience_score": 0.95}},
        status=Status.SUCCESS
    )
    action = fluctuatest_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert "chaos_test_result" in action.result

def test_execute_unstable(fluctuatest_agent, initial_state):
    proposal = AgentTask(
        agent_name="fluctuatest",
        task_type="chaos_test",
        payload={"chaos_test_result": {"resilience_score": 0.4}},
        status=Status.SUCCESS
    )
    action = fluctuatest_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert "chaos_test_result" in action.result
