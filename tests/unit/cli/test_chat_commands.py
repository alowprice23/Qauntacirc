import pytest
from unittest.mock import MagicMock

from cli.commands.chat import ConversationalCLI
from core.types import AppContext, QuantaCircConfig
from rich.console import Console

# A mock for the rich.live.Live object that does nothing
class MockLive:
    def update(self, renderable):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture
def cli_instance():
    """Provides a fresh instance of ConversationalCLI for each test."""
    console = Console()
    config = QuantaCircConfig()
    app_context = AppContext(config=config, console=console, interactive=False, log_level="INFO")
    cli = ConversationalCLI(context=app_context)
    # Disable the energy gate for predictable testing
    cli.router.MAX_PLAN_ENERGY = 1.0
    return cli

@pytest.mark.asyncio
async def test_obligation_creation(cli_instance):
    """
    Tests that processing a command correctly creates and tracks open obligations.
    """
    mock_live = MockLive()
    user_input = "create a new python web api project"

    # Manually add user input to history, since we're bypassing get_user_input
    cli_instance.session.add_history("user", user_input)

    # Process the command that generates obligations
    await cli_instance.process_command(user_input, mock_live)

    # Verify the session state
    session = cli_instance.session
    assert len(session.qc_state.open_obligations) == 4
    assert len(session.qc_state.completed_obligations) == 0

    # Check for a specific obligation string
    assert "Verify task 'init_dir'" in session.qc_state.open_obligations[0]

@pytest.mark.asyncio
async def test_obligation_resolution(cli_instance):
    """
    Tests that the 'resolve' command correctly moves an obligation
    from open to completed.
    """
    mock_live = MockLive()
    # First, create the obligations
    cli_instance.session.add_history("user", "create a new project")
    await cli_instance.process_command("create a new project", mock_live)

    session = cli_instance.session
    assert len(session.qc_state.open_obligations) == 4

    # Now, resolve the first one
    obligation_to_resolve = session.qc_state.open_obligations[0]
    resolve_command = f"resolve {obligation_to_resolve}" # Use the full string for robustness

    await cli_instance.process_command(resolve_command, mock_live)

    # Verify the state change
    assert len(session.qc_state.open_obligations) == 3
    assert len(session.qc_state.completed_obligations) == 1
    assert session.qc_state.completed_obligations[0] == obligation_to_resolve
    assert obligation_to_resolve not in session.qc_state.open_obligations
