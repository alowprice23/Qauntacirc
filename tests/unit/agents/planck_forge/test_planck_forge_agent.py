import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import uuid

from agents.planck_forge.agent import PlanckForgeAgent
from core.types import QCState as State, AgentTask as Proposal, AgentResult as Action, SoftwareState, EnergyComponents, Status
from agents.planck_forge.ops import TaskValidationError

@pytest.fixture
def mock_llm_client():
    client = Mock()
    client.complete = AsyncMock(return_value={"content": "parsed content"})
    return client

@pytest.fixture
def agent(mock_llm_client):
    metrics_logger = Mock()
    metrics_logger.log_duration.return_value = MagicMock()
    return PlanckForgeAgent(
        state_space=Mock(),
        energy_calculator=Mock(),
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
        metadata={"requirement_text": "test requirement"}
    )

@pytest.mark.asyncio
async def test_analyze_state_success(agent, mock_state):
    with patch('agents.planck_forge.agent.prompts') as mock_prompts, \
         patch('agents.planck_forge.agent.ops') as mock_ops:

        mock_prompts.get_prompt.return_value.format.return_value = "formatted prompt"
        mock_ops.parse_llm_output.return_value = [{"task": "1"}]

        proposal = await agent.analyze_state(mock_state)

        assert proposal.status == Status.SUCCESS
        assert proposal.payload["tasks"] == [{"task": "1"}]
        mock_prompts.get_prompt.assert_called_once_with("decompose_requirement", "latest")
        agent.llm_client.complete.assert_awaited_once_with({"prompt": "formatted prompt"})
        mock_ops.parse_llm_output.assert_called_once_with("parsed content")

@pytest.mark.asyncio
async def test_analyze_state_no_requirement(agent, mock_state):
    mock_state.metadata = {}
    proposal = await agent.analyze_state(mock_state)
    assert proposal.status == Status.FAILED
    assert "No requirement text" in proposal.reason

def test_validate_proposal_success(agent):
    with patch('agents.planck_forge.agent.ops.validate_task_set') as mock_validate:
        proposal = Proposal(
            agent_name=agent.name,
            task_type="analysis",
            payload={"tasks": [{"task": "1"}]},
            status=Status.SUCCESS
        )
        assert agent.validate_proposal(proposal) is True
        mock_validate.assert_called_once_with([{"task": "1"}])

def test_validate_proposal_failure(agent):
    with patch('agents.planck_forge.agent.ops.validate_task_set') as mock_validate:
        mock_validate.side_effect = TaskValidationError("Invalid task")
        proposal = Proposal(
            agent_name=agent.name,
            task_type="analysis",
            payload={"tasks": [{"task": "invalid"}]},
            status=Status.SUCCESS
        )
        assert agent.validate_proposal(proposal) is False

def test_execute(agent):
    with patch('agents.planck_forge.agent.ops.generate_task_dag') as mock_generate_dag:
        tasks = [{"task": "1", "dependencies": []}]
        proposal = Proposal(
            id=uuid.uuid4(),
            agent_name=agent.name,
            task_type="analysis",
            payload={"tasks": tasks, "requirement_text": "test req"},
            status=Status.SUCCESS
        )
        mock_generate_dag.return_value = {"nodes": ["1"], "edges": []}
        agent.energy_calculator.compute_static_energy.return_value = 50.0

        action = agent.execute(proposal)

        assert action.status == Status.SUCCESS
        assert action.result["task_dag"] == {"nodes": ["1"], "edges": []}
        assert action.result["energy_impact"]["static"] == 50.0
        mock_generate_dag.assert_called_once_with(tasks)
        agent.energy_calculator.compute_static_energy.assert_called_once()
