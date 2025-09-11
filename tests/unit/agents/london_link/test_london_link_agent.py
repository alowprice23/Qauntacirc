import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.london_link.agent import LondonLinkAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {"content": '{"optimization_actions": [{"package": "requests", "recommended_version": "2.26.0"}]}'}
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_vulnerability_fix": 20.0}
    return calculator

@pytest.fixture
def london_link_agent(mock_llm_client, mock_energy_calculator):
    return LondonLinkAgent(
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
            "dependency_file_content": "requests==2.25.0"
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_success(london_link_agent, initial_state):
    proposal = await london_link_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "optimization_plan" in proposal.payload

def test_execute(london_link_agent):
    proposal = AgentTask(
        agent_name="london_link",
        task_type="dependency_optimization",
        payload={
            "optimization_plan": [{"package": "requests", "reason": "vulnerability"}],
            "dependencies": [{"name": "requests", "version": "2.25.0"}]
        },
    )
    action = london_link_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "optimization_plan" in action.result
    assert "sbom" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["interaction"] < 0
