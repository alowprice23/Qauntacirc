import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.phonon_flow.agent import PhononFlowAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {"content": '{"analysis": "a", "proposed_pattern": "p", "implementation_plan": [], "expected_outcome": "50% improvement"}'}
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_data_flow_efficiency": 1.0}
    return calculator

@pytest.fixture
def phonon_agent(mock_llm_client, mock_energy_calculator):
    return PhononFlowAgent(
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
        metadata={
            "source_code_map": {
                "src/a.py": "import requests\nrequests.get('http://example.com')"
            }
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_success(phonon_agent, initial_state):
    proposal = await phonon_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "optimization_plan" in proposal.payload

def test_execute(phonon_agent):
    proposal = AgentTask(
        agent_name="phonon_flow",
        task_type="optimization",
        payload={
            "optimization_plan": {
                "expected_outcome": "improves by 25%"
            }
        },
    )
    action = phonon_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "optimization_plan" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["interaction"] < 0
