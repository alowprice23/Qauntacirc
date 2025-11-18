import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import uuid

from agents.schrodinger_dev.agent import SchrodingerDevAgent
from core.types import (
    QCState as State,
    AgentTask as Proposal,
    AgentResult as Action,
    SoftwareState,
    EnergyComponents,
    Status,
)
from agents.schrodinger_dev import ops, prompts

@pytest.fixture
def mock_llm_client():
    client = Mock()
    client.complete = AsyncMock(return_value={"content": "mocked code", "confidence": 0.95})
    return client

@pytest.fixture
def agent(mock_llm_client):
    metrics_logger = Mock()
    metrics_logger.log_duration.return_value = MagicMock()
    energy_calculator = Mock()
    energy_calculator.config = {} # Mock config for execute method
    return SchrodingerDevAgent(
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
            "task_dag": {"T01": []},
            "planck_forge_output": {
                "tasks": [{
                    "task_id": "T01",
                    "description": "test task",
                    "verification_criteria": "it works"
                }]
            }
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_success(agent, mock_state):
    with patch('agents.schrodinger_dev.agent.prompts', autospec=True) as mock_prompts, \
         patch('agents.schrodinger_dev.agent.ops', autospec=True) as mock_ops:

        mock_prompts.get_prompt.return_value.format.return_value = "formatted prompt"
        mock_ops.create_code_and_proof_files.return_value = {"file1.py": "code"}

        proposal = await agent.analyze_state(mock_state)

        assert proposal.status == Status.SUCCESS
        assert "generated_files" in proposal.payload
        assert "file1.py" in proposal.payload["generated_files"]
        assert proposal.payload["avg_llm_confidence"] == 0.95

def test_validate_proposal_success(agent):
    with patch('agents.schrodinger_dev.agent.ops.validate_python_syntax') as mock_validate:
        proposal = Proposal(
            agent_name=agent.name,
            task_type="test",
            payload={"generated_files": {"test.py": "print('hello')"}},
            status=Status.SUCCESS
        )
        assert agent.validate_proposal(proposal) is True
        mock_validate.assert_called_once_with("print('hello')")

def test_validate_proposal_failure(agent):
    with patch('agents.schrodinger_dev.agent.ops.validate_python_syntax') as mock_validate:
        mock_validate.side_effect = ops.CodeGenerationError("Invalid syntax")
        proposal = Proposal(
            agent_name=agent.name,
            task_type="test",
            payload={"generated_files": {"test.py": "invalid code"}},
            status=Status.SUCCESS
        )
        assert agent.validate_proposal(proposal) is False

def test_execute(agent):
    with patch('agents.base.ops.parse_to_ast') as mock_parse, \
         patch('agents.base.ops.calculate_cyclomatic_complexity') as mock_complexity:

        mock_parse.return_value = "ast_tree"
        mock_complexity.return_value = 5
        agent.energy_calculator.compute_static_energy.return_value = 50.0

        proposal = Proposal(
            id=uuid.uuid4(),
            agent_name=agent.name,
            task_type="test",
            payload={
                "generated_files": {"test.py": "code"},
                "avg_llm_confidence": 0.8
            },
            status=Status.SUCCESS
        )

        action = agent.execute(proposal)

        assert action.status == Status.SUCCESS
        assert action.result["files_to_create"] == {"test.py": "code"}
        assert action.result["energy_impact"]["static"] == 50.0
        assert action.result["energy_impact"]["dynamic"] > 0
        mock_complexity.assert_called_once_with("ast_tree")
