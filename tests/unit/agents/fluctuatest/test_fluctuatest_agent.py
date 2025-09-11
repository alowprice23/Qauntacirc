import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.fluctuatest.agent import FluctuaTestAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

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
    software_state = SoftwareState(component_versions={}, config_hashes={}, status="initial")
    energy_components = EnergyComponents(static=100.0, dynamic=50.0, interaction=20.0)
    return QCState(
        software_state=software_state,
        energy=energy_components.total,
        energy_components=energy_components,
        lyapunov_potential=170.0,
        contraction_factor=1.0,
    )

@pytest.mark.asyncio
async def test_analyze_state_success(fluctuatest_agent, initial_state):
    proposal = await fluctuatest_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "experiment" in proposal.payload
    assert proposal.payload["experiment"]["experiment_type"] == "latency_injection"

def test_execute_stable(fluctuatest_agent, initial_state):
    proposal = AgentTask(
        agent_name="fluctuatest",
        task_type="chaos_test",
        payload={"experiment": {"experiment_type": "latency_injection", "magnitude": 10}},
        quantum_context=initial_state
    )
    action = fluctuatest_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert action.result["is_stable"] is True
    assert action.result["energy_impact"]["debt"] == 0

def test_execute_unstable(fluctuatest_agent, initial_state):
    proposal = AgentTask(
        agent_name="fluctuatest",
        task_type="chaos_test",
        payload={"experiment": {"experiment_type": "latency_injection", "magnitude": 100}},
        quantum_context=initial_state
    )
    action = fluctuatest_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert action.result["is_stable"] is False
    assert action.result["energy_impact"]["debt"] > 0
