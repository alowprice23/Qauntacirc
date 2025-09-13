import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock
from agents.schrodinger_dev.agent import SchrodingerDevAgent
from core.data_models import SystemState, AgentTask, EnergyBreakdown, LyapunovMetrics, Status, CodeEvolution, CodeState, UnitaryOperator, SoftwareState

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.side_effect = [
        {"content": "```python\ndef func_a(): pass\n```\n```python\ndef func_b(): pass\n```"},
        {"content": "```python\nassert True\n```"}
    ]
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
    # Refactored to create a valid SystemState object
    energy_breakdown = EnergyBreakdown(total=170.0, complexity=100.0, coupling=50.0, constraint=20.0, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=170.0, energy=170.0, test_penalty=0.0, obligation_penalty=0.0)
    return SystemState(
        software_state=SoftwareState(),
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
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
    proposal = schrodinger_agent.analyze_state(initial_state)
    assert proposal.status == Status.SUCCESS
    assert "code_evolution" in proposal.payload

@pytest.mark.asyncio
async def test_analyze_state_no_task_dag(schrodinger_agent, initial_state):
    initial_state.metadata = {}
    proposal = schrodinger_agent.analyze_state(initial_state)
    assert proposal.status == Status.FAILED
    assert "Task DAG or task list not found" in proposal.reason

def test_execute(schrodinger_agent):
    # Create a realistic proposal for the execute method
    mock_evolution = CodeEvolution(
        new_state=CodeState(state_vector=np.random.rand(4), code="..."),
        proofs=[],
        energy_change=0.1,
        unitary_operator=UnitaryOperator(matrix=np.identity(4))
    )

    proposal = AgentTask(
        agent_name="schrodinger_dev",
        task_type="code_evolution",
        payload={"code_evolution": mock_evolution.model_dump()},
        status=Status.SUCCESS
    )

    action = schrodinger_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert action.result == proposal.payload
