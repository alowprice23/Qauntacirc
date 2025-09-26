import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from typer.testing import CliRunner

from cli.commands.orchestrator import app as orchestrator_app
from core.orchestrator import Orchestrator
from core.system_state import SystemState

# A mock NATS client that can be awaited
async def mock_nats_connect(*args, **kwargs):
    return AsyncMock()

class TestCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('nats.connect', new_callable=lambda: mock_nats_connect)
    @patch('core.orchestrator.Orchestrator.run')
    def test_run_command(self, mock_orchestrator_run, mock_nats):
        """Test the main `qcli orchestrator run` command."""
        # Mock the orchestrator's run method to return a predictable state
        mock_orchestrator_run.return_value = asyncio.Future()
        mock_orchestrator_run.return_value.set_result(SystemState(data={"final": "state"}))

        result = self.runner.invoke(orchestrator_app, ["run", "my-test-task"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Starting orchestrator run", result.stdout)
        self.assertIn("Final state", result.stdout)
        self.assertIn("'final': 'state'", result.stdout)

    @patch('nats.connect', new_callable=lambda: mock_nats_connect)
    def test_dry_run_command(self, mock_nats):
        """Test the `qcli orchestrator dry-run` command."""
        result = self.runner.invoke(orchestrator_app, ["dry-run"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Orchestrator Dry Run", result.stdout)
        self.assertIn("Execution Plan", result.stdout)
        self.assertIn("planck_forge", result.stdout)
        self.assertIn("schrodinger_dev", result.stdout)

    @patch('nats.connect', new_callable=lambda: mock_nats_connect)
    def test_dry_run_show_dependencies(self, mock_nats):
        """Test the `qcli orchestrator dry-run --show-dependencies` command."""
        result = self.runner.invoke(orchestrator_app, ["dry-run", "--show-dependencies"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Agent Dependencies", result.stdout)
        self.assertIn("Inputs", result.stdout)
        self.assertIn("Outputs", result.stdout)
        self.assertIn("planck_forge", result.stdout)
        self.assertIn("quantized_tasks", result.stdout)

    @patch('nats.connect', new_callable=lambda: mock_nats_connect)
    @patch('core.orchestrator.Orchestrator.run')
    def test_simulate_failure_command(self, mock_orchestrator_run, mock_nats):
        """Test the `qcli orchestrator run --simulate-failure` command."""
        mock_orchestrator_run.return_value = asyncio.Future()
        mock_orchestrator_run.return_value.set_result(SystemState(data={"recovered": True}))

        result = self.runner.invoke(orchestrator_app, ["run", "task", "--simulate-failure", "pauli_guard"])

        self.assertEqual(result.exit_code, 0)

        # Check that the orchestrator's run method was called with the correct `simulate_failure` value
        # The first argument to run is `self`, so we check the kwargs of the call
        call_args = mock_orchestrator_run.call_args
        self.assertIn('simulate_failure', call_args.kwargs)
        self.assertEqual(call_args.kwargs['simulate_failure'], 'pauli_guard')


if __name__ == '__main__':
    unittest.main()