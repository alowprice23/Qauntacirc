import typer
from rich.console import Console
from rich.theme import Theme
from typing import Optional, Any
from pathlib import Path

from core.types import AppContext, QuantaCircConfig
from core.config_loader import load_config
from core.exceptions import QuantaCircError
from monitoring.logging import setup_logging
from monitoring.metrics import initialize_metrics

def get_app_context(
    config_path: Optional[Path] = None,
    log_level: str = "INFO",
    non_interactive: bool = False,
    console: Console = None,
) -> AppContext:
    print(f"get_app_context called with: config_path={config_path}, log_level={log_level}, non_interactive={non_interactive}")
    """
    Get the application context.
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

        # Verify quantum state consistency on startup
        if not app_context.verify_quantum_state():
            console.print("[warning]Quantum state inconsistency detected[/warning]")
            if app_context.interactive:
                if not typer.confirm("Continue anyway?"):
                    raise typer.Exit(1)

        return app_context

    except QuantaCircError as e:
        console.print(f"[error]QuantaCirc Error: {e.message}[/error]")
        if hasattr(e, 'suggested_fix') and e.suggested_fix:
            console.print(f"[warning]Suggested fix: {e.suggested_fix}[/warning]")
        raise typer.Exit(1)
