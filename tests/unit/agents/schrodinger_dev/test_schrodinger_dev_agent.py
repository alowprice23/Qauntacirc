import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.schrodinger_dev.agent import SchrodingerDevAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {"content": "```python\nprint('hello')\n```", "confidence": 0.9}
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_code_quality": 1.0}
    calculator.compute_static_energy.return_value = 10.0
    return calculator

@pytest.fixture
def schrodinger_agent(mock_llm_client, mock_energy_calculator):
    return SchrodingerDevAgent(
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
            "planck_forge_output": {
                "tasks": [
                    {"id": "task1", "description": "d1", "verification_criteria": ["vc1"]},
                ]
            },
            "task_dag": {"task1": []}
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_success(schrodinger_agent, initial_state):
    proposal = await schrodinger_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "generated_files" in proposal.payload
    assert "avg_llm_confidence" in proposal.payload
    assert proposal.payload["avg_llm_confidence"] == pytest.approx(0.9)

@pytest.mark.asyncio
async def test_analyze_state_no_task_dag(schrodinger_agent, initial_state):
    initial_state.metadata = {}
    proposal = await schrodinger_agent.analyze_state(initial_state)
    assert proposal.status == "FAILED"
    assert "Task DAG or task list not found" in proposal.reason

def test_execute(schrodinger_agent):
    proposal = AgentTask(
        agent_name="schrodinger_dev",
        task_type="analysis",
        payload={
            "generated_files": {"src/test.py": "print('test')"},
            "avg_llm_confidence": 0.8
        },
    )
    action = schrodinger_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "files_to_create" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["dynamic"] == pytest.approx(20.0)
