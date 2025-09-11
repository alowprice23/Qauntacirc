import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.phonon_flow.agent import PhononFlowAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {
        "content": '{"refactored_code": "new code here", "explanation": "did a thing"}'
    }
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_maintainability": 5.0}
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
    """A state with two files, one of which is clearly 'slower'."""
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
                # High density, high coupling -> low v_s
                "src/slow.py": "import src.fast\n" + "\n".join(["if x: pass" for _ in range(10)]),
                # Low density, low coupling -> high v_s
                "src/fast.py": "x = 1"
            }
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_targets_slowest_file(phonon_agent, initial_state):
    proposal = await phonon_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert proposal.payload["file_to_update"] == "src/slow.py"
    assert "refactored_code" in proposal.payload

def test_execute_calculates_energy_impact(phonon_agent):
    proposal = AgentTask(
        agent_name="phonon_flow",
        task_type="refactoring",
        payload={
            "file_to_update": "src/slow.py",
            "refactored_code": "x=1\ny=2" # Low density code
        },
    )
    action = phonon_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "refactoring_plan" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["interaction"] < 0
