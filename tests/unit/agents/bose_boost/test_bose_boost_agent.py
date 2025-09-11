import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.bose_boost.agent import BoseBoostAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents, TaskQuanta

@pytest.fixture
def mock_llm_client():
    return AsyncMock()

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_replicas": 1.0}
    return calculator

@pytest.fixture
def bose_agent(mock_llm_client, mock_energy_calculator):
    return BoseBoostAgent(
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
async def test_analyze_state_success(bose_agent, initial_state):
    proposal = await bose_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "deployment_manifests" in proposal.payload
    assert len(proposal.payload["deployment_manifests"]) == 2

def test_execute(bose_agent):
    proposal = AgentTask(
        agent_name="bose_boost",
        task_type="scaling",
        payload={
            "deployment_manifests": {"task1": "manifest1", "task2": "manifest2"}
        },
    )
    action = bose_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "deployment_manifests" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["debt"] > 0
