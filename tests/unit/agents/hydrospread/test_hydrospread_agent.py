import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.hydro_spread.agent import HydroSpreadAgent
from core.data_models import SystemState, AgentTask, EnergyBreakdown, LyapunovMetrics, Status, Module, SoftwareState
from datetime import datetime

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {"content": '{"summary": "s", "explanation": "e", "recommendations": []}'}
    return client

@pytest.fixture
def hydrospread_agent(mock_llm_client):
    return HydroSpreadAgent(
        state_space=MagicMock(),
        energy_calculator=MagicMock(),
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
        module_count=10,
        team_size=5,
        total_complexity=50.0,
        coupling_density=0.2,
        current_volume=100.0
    )

@pytest.mark.asyncio
async def test_analyze_state_success(hydrospread_agent, initial_state):
    proposal = hydrospread_agent.analyze_state(initial_state)
    assert proposal.status == Status.SUCCESS
    assert "growth_prediction" in proposal.payload
    prediction = proposal.payload["growth_prediction"]
    assert len(prediction["predictions"]) > 0
    assert "viscosity" in prediction

def test_execute(hydrospread_agent):
    proposal = AgentTask(
        agent_name="hydrospread",
        task_type="forecast",
        payload={"growth_prediction": {"predictions": []}},
        status=Status.SUCCESS
    )
    action = hydrospread_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert "growth_prediction" in action.result
