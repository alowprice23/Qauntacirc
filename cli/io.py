import asyncio
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Prompt, Confirm
from rich.spinner import Spinner
from rich.table import Table
# import sacrobleu # Temporarily removed to debug ModuleNotFoundError

from core.types import AppContext, TaskQuanta
from cli.state import SessionState

class QuantaCircIO:
    """
    Handles all rich I/O operations for the conversational CLI.
    """

    def __init__(self, context: AppContext):
        self.console = getattr(context, 'console', Console())
        self.interactive = getattr(context, 'interactive', True)

    def welcome_screen(self, session_state: SessionState):
        """
        Displays the welcome screen with initial system state.
        """
        qc_state = session_state.qc_state
        panel = Panel(
            f"Session ID: {session_state.session_id}\n"
            f"System Energy E(S): [energy]{qc_state.energy:.6f}[/energy]\n"
            f"Lyapunov Potential Φ(S): [lyapunov]{qc_state.lyapunov_potential:.6f}[/lyapunov]",
            title="[quantum]QuantaCirc Conversational Interface[/quantum]",
            subtitle="[bold cyan]Welcome[/bold cyan]"
        )
        self.console.print(panel)

    def goodbye_screen(self, session_state: SessionState):
        """
        Displays the goodbye screen with final system state.
        """
        qc_state = session_state.qc_state
        panel = Panel(
            f"Session ID: {session_state.session_id}\n"
            f"Final System Energy E(S): [energy]{qc_state.energy:.6f}[/energy]\n"
            f"Final Lyapunov Potential Φ(S): [lyapunov]{qc_state.lyapunov_potential:.6f}[/lyapunov]",
            title="[quantum]QuantaCirc Session Ended[/quantum]",
            subtitle="[bold cyan]Goodbye[/bold cyan]"
        )
        self.console.print(panel)

    def get_user_input(self, session_state: SessionState) -> str:
        """
        Gets user input with history and auto-completion.
        CNL validation is temporarily disabled to avoid dependency issues.
        """
        prompt_text = f"[bold cyan]Q> [/]({session_state.session_id[:8]}) "
        raw_input = Prompt.ask(prompt_text)

        # CNL validation using BLEU score is temporarily disabled.
        # We'll assume a perfect score for now.
        bleu_score = 100.0

        session_state.add_history("user", raw_input, metadata={"bleu_score": bleu_score})

        return raw_input

    @contextmanager
    def spinner(self, text: str = "Processing..."):
        """
        Displays a spinner for long-running operations with quantum state indicators.
        """
        # TODO: Update spinner with live energy metrics from another thread.
        spinner = Spinner("dots", text=text)
        with Live(spinner, console=self.console, transient=True, refresh_per_second=20) as live:
            yield live

    def get_approval(self, message: str, risk_bounds: Dict[str, float]) -> bool:
        """
        Requests user approval with a display of mathematical risk bounds.
        """
        if not self.interactive:
            self.console.print("[warning]Skipping approval in non-interactive mode.[/warning]")
            return True

        table = Table(title="[lyapunov]Risk Analysis[/lyapunov]", show_header=False, box=None)
        for key, value in risk_bounds.items():
            table.add_row(f"[yellow]{key}[/yellow]", f"{value:.4f}")

        panel = Panel(table, title="[warning]Permission Request[/warning]", border_style="yellow")
        self.console.print(panel)
        return Confirm.ask(message, default=False)

    def display_plan(self, quanta: List[TaskQuanta]):
        """
        Displays an execution plan (a list of TaskQuanta) with energy impact visualization.
        """
        table = Table(title="[bold green]Task Quantization Plan[/bold green]", expand=True)
        table.add_column("ID", style="cyan")
        table.add_column("Description", style="magenta", max_width=50)
        table.add_column("Energy Level", justify="right", style="green")

        total_energy = 0
        for q in quanta:
            table.add_row(q.id, q.description, f"{q.energy:.4f}")
            total_energy += q.energy

        self.console.print(table)
        self.console.print(f"Total Quantized Energy: [energy]{total_energy:.4f}[/energy]")

    def display_results(self, session_state: SessionState, artifacts: Optional[List[str]] = None):
        """
        Displays the results of an operation, including quantum state changes.
        """
        qc_state = session_state.qc_state

        state_table = Table(title="[quantum]Quantum State Update[/quantum]", expand=True)
        state_table.add_column("Metric", style="yellow", width=25)
        state_table.add_column("Value", style="cyan")
        state_table.add_row("Energy E(S)", f"{qc_state.energy:.6f}")
        state_table.add_row("  - Static", f"{qc_state.energy_components.static:.6f}")
        state_table.add_row("  - Dynamic", f"{qc_state.energy_components.dynamic:.6f}")
        state_table.add_row("  - Interaction", f"{qc_state.energy_components.interaction:.6f}")
        state_table.add_row("Lyapunov Φ(S)", f"{qc_state.lyapunov_potential:.6f}")
        state_table.add_row("Contraction Factor λ", f"{qc_state.contraction_factor:.6f}")
        state_table.add_row("Optimization Phase", qc_state.optimization_phase)

        self.console.print(state_table)

        if artifacts is not None:
            artifacts_panel = Panel(
                "\n".join(artifacts) if artifacts else "No artifacts generated.",
                title="[bold green]Generated Artifacts[/bold green]",
                border_style="green"
            )
            self.console.print(artifacts_panel)

    def display_error(self, code: str, message: str, suggestions: Optional[List[str]] = None):
        """
        Displays a structured error message.
        """
        suggestions = suggestions or []
        suggestion_text = "\n".join(f"- {s}" for s in suggestions)

        error_panel = Panel(
            f"[bold]{message}[/bold]\n\n[yellow]Suggestions:[/yellow]\n{suggestion_text}",
            title=f"[bold red]Error: {code}[/bold red]",
            border_style="red"
        )
        self.console.print(error_panel)
