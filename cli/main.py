import typer
from rich.console import Console
from rich.theme import Theme
from typing import Optional, Any
import sys
import os
from pathlib import Path

from . import __version__
from .commands import init, generate, verify, deploy, demo, status, memory, chat
from core.types import AppContext, QuantaCircConfig
from core.config_loader import load_config
from core.exceptions import QuantaCircError
from monitoring.logging import setup_logging
from monitoring.metrics import initialize_metrics

# Rich console with QuantaCirc theme
console = Console(theme=Theme({
    "quantum": "bold blue",
    "energy": "bold green",
    "lyapunov": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "warning": "bold yellow"
}))

app = typer.Typer(
    name="qc",
    help="QuantaCirc: Quantum-Mechanical Software Engineering System",
    epilog="For detailed documentation, visit: https://docs.quantacirc.org",
    add_completion=False,
    rich_markup_mode="rich"
)

def version_callback(value: bool):
    """Handle --version flag with rich formatting"""
    if value:
        console.print(f"[quantum]QuantaCirc[/quantum] v{__version__}")
        console.print("Quantum-Mechanical Software Engineering System")
        raise typer.Exit()

@app.callback()
def main(
    ctx: typer.Context,
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to quantacirc.yml configuration file"
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Logging level (DEBUG, INFO, WARNING, ERROR)"
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Disable interactive prompts"
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    )
):
    """
    Initialize QuantaCirc application context and global configuration.
    
    This callback runs before any subcommand, establishing the quantum
    state monitoring, formal verification framework, and agent orchestration.
    """
    try:
        # Setup structured logging first
        setup_logging(level=log_level)

        # Load configuration
        if config_path and not config_path.exists():
            console.print(f"[error]Configuration file not found: {config_path}[/error]")
            raise typer.Exit(1)

        config = load_config(config_path)

        # Initialize metrics collection
        initialize_metrics(config=config)
        app_context = AppContext(
            config=config,
            console=console,
            interactive=not non_interactive,
            log_level=log_level
        )

        # Store in Typer context for subcommands
        ctx.obj = app_context

        # Verify quantum state consistency on startup
        if not app_context.verify_quantum_state():
            console.print("[warning]Quantum state inconsistency detected[/warning]")
            if app_context.interactive:
                if not typer.confirm("Continue anyway?"):
                    raise typer.Exit(1)

    except QuantaCircError as e:
        console.print(f"[error]QuantaCirc Error: {e.message}[/error]")
        if hasattr(e, 'suggested_fix') and e.suggested_fix:
            console.print(f"[warning]Suggested fix: {e.suggested_fix}[/warning]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[error]Unexpected error: {str(e)}[/error]")
        raise typer.Exit(1)


# Register all subcommands
app.add_typer(init.app, name="init", help="Initialize new QuantaCirc project")
app.add_typer(generate.app, name="generate", help="Generate code using agent pipeline")
app.add_typer(verify.app, name="verify", help="Run formal verification checks")
app.add_typer(deploy.app, name="deploy", help="Deploy to target environment")
app.add_typer(demo.app, name="demo", help="Run demonstration scenarios")
app.add_typer(status.app, name="status", help="Display system quantum state")
app.add_typer(memory.app, name="memory", help="Interact with Constellation memory")
app.add_typer(chat.app, name="chat", help="Start a conversational session")

if __name__ == "__main__":
    app()
