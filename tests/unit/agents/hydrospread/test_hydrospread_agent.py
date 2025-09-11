import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.hydrospread.agent import HydroSpreadAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents, TaskQuanta

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
    software_state = SoftwareState(component_versions={}, config_hashes={}, status="initial")
    energy_components = EnergyComponents(static=100.0, dynamic=50.0, interaction=20.0)
    tasks = [
        TaskQuanta(id="task1", description="d1", verification_criteria=["vc1"], energy=20.0),
        TaskQuanta(id="task2", description="d2", verification_criteria=["vc2"], energy=80.0),
    ]
    return QCState(
        software_state=software_state,
        energy=energy_components.total,
        energy_components=energy_components,
        lyapunov_potential=170.0,
        contraction_factor=1.0,
        metadata={
            "planck_forge_output": {
                "tasks": tasks
            }
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_success(hydrospread_agent, initial_state):
    proposal = await hydrospread_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "forecast_report" in proposal.payload

def test_execute(hydrospread_agent):
    proposal = AgentTask(
        agent_name="hydrospread",
        task_type="forecast",
        payload={"forecast_report": "{}"},
    )
    action = hydrospread_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "forecast_report" in action.result
    assert not action.result["energy_impact"] # No energy impact
