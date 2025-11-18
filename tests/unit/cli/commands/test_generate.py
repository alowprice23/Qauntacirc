import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from cli.commands.generate import app

runner = CliRunner()

@patch('cli.commands.generate.generation_counter')
@patch('cli.commands.generate.generation_duration')
def test_requirement_command(mock_duration, mock_counter):
    # This test only checks the initial part of the command,
    # as the rest is commented out.
    result = runner.invoke(app, ["requirement", "test req"])

    assert result.exit_code == 0
    assert "Processing requirement: test req" in result.stdout
    mock_counter.inc.assert_called_once()
    mock_duration.time.assert_called_once()

def test_status_command():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Showing generation pipeline status..." in result.stdout

def test_cancel_command():
    result = runner.invoke(app, ["cancel", "--job-id", "job_123"])
    assert result.exit_code == 0
    assert "Cancelling generation job job_123..." in result.stdout
