import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

import sacrebleu
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
from rich.prompt import Confirm
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.styles import Style

from core.types import AppContext, TaskQuanta
from cli.state import SessionState

# Define a custom style for the prompt
prompt_style = Style.from_dict({
    'prompt': 'bold cyan',
})

class QuantaCircIO:
    """
    Handles all rich I/O operations for the conversational CLI.
    """

    def __init__(self, context: AppContext):
        self.console = getattr(context, 'console', Console())
        self.interactive = getattr(context, 'interactive', True)

        # Setup prompt_toolkit session with history
        history_path = Path(os.path.expanduser("~/.quantacirc/history.txt"))
        history_path.parent.mkdir(parents=True, exist_ok=True)
        self.prompt_session = PromptSession(
            history=FileHistory(str(history_path))
        )

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

    def get_user_input(self, session_state: SessionState, bottom_toolbar: Optional[Callable] = None) -> str:
        """
        Gets user input with history, auto-completion, and BLEU score validation.
        """
        prompt_text = [('class:prompt', f"Q> ({session_state.session_id[:8]}) ")]

        def get_toolbar():
            if bottom_toolbar:
                return Text.from_markup(bottom_toolbar())
            return None

        while True:
            raw_input = self.prompt_session.prompt(
                prompt_text,
                completer=PathCompleter(),
                style=prompt_style,
                bottom_toolbar=get_toolbar,
                refresh_interval=0.5
            )

            # --- BLEU Score Validation ---
            # A simple reference for what we expect. In a real system, this would be
            # more sophisticated, perhaps generated based on the current context.
            cnl_reference = "create a new project"
            bleu = sacrebleu.corpus_bleu(raw_input, [cnl_reference])
            bleu_score = bleu.score

            session_state.add_history("user", raw_input, metadata={"bleu_score": bleu_score})

            if bleu_score >= 90: # Auto-accept (using 0.90 scale from prompt, so 90 for sacrebleu)
                return raw_input
            elif 70 <= bleu_score < 90:
                if not self.interactive:
                    self.console.print("[yellow]Warning: Low clarity input in non-interactive mode. Proceeding.[/yellow]")
                    return raw_input

                if Confirm.ask(
                    f"[yellow]Your command has a low clarity score (BLEU: {bleu_score:.2f}). Proceed anyway?[/yellow]",
                    default=True
                ):
                    return raw_input
                else:
                    self.console.print("[bold cyan]Please rephrase your command.[/bold cyan]")
                    continue # Ask for input again
            else: # < 70
                if not self.interactive:
                    raise ValueError(f"Input clarity too low (BLEU: {bleu_score:.2f}). Aborting in non-interactive mode.")

                self.display_error(
                    "QCE-CLI-003",
                    f"Input clarity is too low to proceed (BLEU: {bleu_score:.2f}).",
                    ["Please try rephrasing your command in simpler terms.", "Focus on one action and one subject."]
                )
                continue # Ask for input again


    @asynccontextmanager
    async def spinner(self, text: str = "Processing..."):
        """
        Displays a spinner for long-running operations with quantum state indicators.
        """
        spinner_text = Text(text, style="yellow")
        spinner = Spinner("dots", text=spinner_text)
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

        table.caption = f"Total Quantized Energy: [energy]{total_energy:.4f}[/energy]"
        return table

    def display_results(self, session_state: SessionState, artifacts: Optional[List[str]] = None):
        """
        Displays the results of an operation, including quantum state changes.
        Returns a Rich renderable.
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

        return state_table


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
