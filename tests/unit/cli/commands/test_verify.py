import pytest
from typer.testing import CliRunner
from unittest.mock import patch

from cli.commands.verify import app

runner = CliRunner()

@patch('cli.commands.verify.Progress')
def test_all_command(mock_progress):
    # This test only checks the initial part of the command,
    # as the rest is commented out.
    result = runner.invoke(app, ["all"])

    assert result.exit_code == 0
    assert "QuantaCirc Formal Verification Suite" in result.stdout
    assert "SMT constraints verified (mocked)" in result.stdout
    assert "Coq proofs validated (mocked)" in result.stdout
    assert "Energy function properties verified (mocked)" in result.stdout
    assert "Closure rules validated (mocked)" in result.stdout
    mock_progress.assert_called_once()

def test_proofs_command():
    result = runner.invoke(app, ["proofs", "--proof-type", "coq"])
    assert result.exit_code == 0
    assert "Verifying coq proofs... (mocked)" in result.stdout

def test_energy_command():
    result = runner.invoke(app, ["energy"])
    assert result.exit_code == 0
    assert "Verifying energy function properties... (mocked)" in result.stdout

def test_constraints_command():
    result = runner.invoke(app, ["constraints"])
    assert result.exit_code == 0
    assert "Verifying SMT constraints... (mocked)" in result.stdout
