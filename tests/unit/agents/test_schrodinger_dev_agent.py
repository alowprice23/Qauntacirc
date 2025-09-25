import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agents.schrodinger_dev.agent import SchrodingerDevAgent
from core.types import QuantaCircConfig, AgentTask, LLMConfig, Status

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_config():
    """Fixture for a mock QuantaCircConfig."""
    llm_config = LLMConfig(provider="mock_provider")
    return QuantaCircConfig(llm=llm_config)

@pytest.fixture
def schrodinger_agent(mock_config):
    """Fixture for a SchrodingerDevAgent instance with a mocked LLM client."""
    with patch('agents.base.agent.get_llm_client') as mock_get_llm:
        # Prevent LLM clients from being created in the constructor
        mock_get_llm.return_value = MagicMock()
        agent = SchrodingerDevAgent(config=mock_config)
        # Mock the high-level fallback method
        agent.llm_generate_with_fallback = AsyncMock()
        return agent

async def test_process_task_success(schrodinger_agent):
    """
    Test that the agent successfully processes a code generation task.
    """
    # Arrange
    task_description = "Create a function that adds two numbers."
    mock_code = "def add(a, b):\n    return a + b"
    mock_llm_response = f"```python\n{mock_code}\n```"
    schrodinger_agent.llm_generate_with_fallback.return_value = mock_llm_response

    task = AgentTask(
        agent_name="SchrodingerDev",
        task_type="code_generation",
        payload={"description": task_description}
    )

    # Act
    result = await schrodinger_agent.process_task(task)

    # Assert
    assert result.status == Status.SUCCESS
    assert result.action_taken is True
    assert result.result["generated_code"] == mock_code

    # Verify that the LLM was called with the correct parameters
    schrodinger_agent.llm_generate_with_fallback.assert_awaited_once()
    call_args, call_kwargs = schrodinger_agent.llm_generate_with_fallback.call_args

    # Check that the prompt contains the task description
    prompt_arg = call_args[0]
    assert task_description in prompt_arg

    # Check that the temperature was set for deterministic output
    assert call_kwargs.get("temperature") == 0.0

async def test_process_task_llm_failure(schrodinger_agent):
    """
    Test how the agent handles a failure from the LLM client.
    """
    # Arrange
    schrodinger_agent.llm_generate_with_fallback.side_effect = RuntimeError("All LLM clients failed")

    task = AgentTask(
        agent_name="SchrodingerDev",
        task_type="code_generation",
        payload={"description": "A task that will fail"}
    )

    # Act
    result = await schrodinger_agent.process_task(task)

    # Assert
    assert result.status == Status.FAILED
    assert result.action_taken is False
    assert "All LLM clients failed" in result.error

async def test_process_task_invalid_code(schrodinger_agent):
    """
    Test that the agent fails gracefully when the LLM returns invalid code.
    """
    # Arrange
    invalid_code = "def add(a, b):\n  return a +"
    mock_llm_response = f"```python\n{invalid_code}\n```"
    schrodinger_agent.llm_generate_with_fallback.return_value = mock_llm_response

    task = AgentTask(
        agent_name="SchrodingerDev",
        task_type="code_generation",
        payload={"description": "A task that returns invalid code"}
    )

    # Act
    result = await schrodinger_agent.process_task(task)

    # Assert
    assert result.status == Status.FAILED
    assert result.action_taken is False
    assert "Generated code has a syntax error" in result.error

async def test_process_task_no_description(schrodinger_agent):
    """
    Test that the agent handles a task with a missing description.
    """
    # Arrange
    task = AgentTask(
        agent_name="SchrodingerDev",
        task_type="code_generation",
        payload={} # Missing "description"
    )

    # Act
    result = await schrodinger_agent.process_task(task)

    # Assert
    assert result.status == Status.FAILED
    assert result.action_taken is False
    assert "Task payload must contain a 'description'" in result.error
    schrodinger_agent.llm_generate_with_fallback.assert_not_called()