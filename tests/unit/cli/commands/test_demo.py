import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from cli.commands.demo import app

runner = CliRunner()

@pytest.fixture
def mock_scenarios():
    return {
        "test_scenario": {
            "description": "A test scenario.",
            "estimated_duration": "5m",
            "agents_used": ["agent1", "agent2"],
            "overview": "This is an overview."
        }
    }

def test_list_demos(mock_scenarios):
    with patch('cli.commands.demo.DEMO_SCENARIOS', mock_scenarios):
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "A test scenario." in result.stdout
        assert "agent1, agent2" in result.stdout

from unittest.mock import patch, MagicMock, AsyncMock

@patch('cli.commands.demo.DemoRunner')
def test_run_demo_success(mock_demo_runner, mock_scenarios):
    mock_runner_instance = mock_demo_runner.return_value
    mock_runner_instance.execute = AsyncMock(return_value=MagicMock(metrics=None))

    with patch('cli.commands.demo.DEMO_SCENARIOS', mock_scenarios):
        result = runner.invoke(app, ["run", "test_scenario", "--automated"])
        assert result.exit_code == 0
        assert "Running Demo: test_scenario" in result.stdout
        mock_demo_runner.assert_called_once()
        mock_runner_instance.execute.assert_awaited_once()

def test_run_demo_nonexistent_scenario():
    result = runner.invoke(app, ["run", "nonexistent"])
    assert result.exit_code == 1
    assert "Unknown scenario" in result.stdout

@patch('cli.commands.demo.DemoRunner')
def test_run_demo_fail(mock_demo_runner, mock_scenarios):
    mock_runner_instance = mock_demo_runner.return_value
    mock_runner_instance.execute = AsyncMock(side_effect=Exception("Demo failed"))

    with patch('cli.commands.demo.DEMO_SCENARIOS', mock_scenarios):
        result = runner.invoke(app, ["run", "test_scenario", "--automated"])
        assert result.exit_code == 1
        assert "Demo failed: Demo failed" in result.stdout
