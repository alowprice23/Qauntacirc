import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import uuid

from agents.pauli_guard.agent import PauliGuardAgent
from core.types import (
    QCState as State,
    AgentTask as Proposal,
    AgentResult as Action,
    SoftwareState,
    EnergyComponents,
    Status,
)
from agents.pauli_guard import ops, prompts

@pytest.fixture
def mock_llm_client():
    client = Mock()
    client.complete = AsyncMock(return_value={"content": '{"plan": "test plan"}'})
    return client

@pytest.fixture
def agent(mock_llm_client):
    metrics_logger = Mock()
    metrics_logger.log_duration.return_value = MagicMock()
    energy_calculator = Mock()
    energy_calculator.config = {}
    return PauliGuardAgent(
        state_space=Mock(),
        energy_calculator=energy_calculator,
        metrics_logger=metrics_logger,
        policy_engine=Mock(),
        agent_memory=Mock(),
        llm_client=mock_llm_client,
    )

@pytest.fixture
def mock_state():
    return State(
        software_state=SoftwareState(component_versions={}, config_hashes={}, status='nominal'),
        energy=0.0,
        energy_components=EnergyComponents(static=0.0, dynamic=0.0, interaction=0.0),
        lyapunov_potential=0.0,
        contraction_factor=1.0,
        metadata={
            "schrodinger_dev_output": {
                "files_to_create": {"file1.py": "code", "file2.py": "code"}
            }
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_with_duplicates(agent, mock_state):
    with patch('agents.pauli_guard.agent.ops', autospec=True) as mock_ops, \
         patch('agents.pauli_guard.agent.prompts', autospec=True) as mock_prompts:

        mock_ops.detect_duplicates.return_value = [{"block_1": {"file_path": "file1.py", "content": "code"}, "block_2": {"file_path": "file2.py", "content": "code"}}]
        mock_prompts.get_prompt.return_value.format.return_value = "formatted prompt"
        mock_ops.parse_refactoring_plan.return_value = {"plan": "test plan"}

        proposal = await agent.analyze_state(mock_state)

        assert proposal.status == Status.SUCCESS
        assert len(proposal.payload["refactoring_plans"]) == 1
        assert proposal.payload["refactoring_plans"][0] == {"plan": "test plan"}

@pytest.mark.asyncio
async def test_analyze_state_no_duplicates(agent, mock_state):
    with patch('agents.pauli_guard.agent.ops.detect_duplicates') as mock_detect:
        mock_detect.return_value = []
        proposal = await agent.analyze_state(mock_state)
        assert proposal.status == Status.SUCCESS
        assert proposal.payload["refactoring_plans"] == []

def test_validate_proposal_success(agent):
    with patch('agents.pauli_guard.agent.ops.parse_refactoring_plan') as mock_parse:
        proposal = Proposal(
            agent_name=agent.name,
            task_type="test",
            payload={"refactoring_plans": [{"plan": "test"}]},
            status=Status.SUCCESS
        )
        assert agent.validate_proposal(proposal) is True
        mock_parse.assert_called_once()

def test_execute(agent):
    proposal = Proposal(
        id=uuid.uuid4(),
        agent_name=agent.name,
        task_type="test",
        payload={
            "refactoring_plans": [],
            "duplicates_found": [{"block_1": {"content": "a" * 10}, "block_2": {"content": "b" * 20}}]
        },
        status=Status.SUCCESS
    )

    action = agent.execute(proposal)

    assert action.status == Status.SUCCESS
    assert "refactoring_plans" in action.result
    assert action.result["energy_impact"]["interaction"] < 0
