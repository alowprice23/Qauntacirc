import typer
import asyncio
import json
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.console import Group
from rich.text import Text

from cli.state import SessionState
from cli.io import QuantaCircIO
from cli.router import CommandRouter
import numpy as np
from core.mathematics import (
    calculate_lyapunov_potential,
    software_to_quantum_functor
)
from core.types import AppContext, QuantumState

app = typer.Typer(
    name="chat",
    help="Start a conversational session with the QuantaCirc agent."
)

class ConversationalCLI:
    """Manages the interactive conversational session with a live display."""
    def __init__(self, context: AppContext):
        self.app_context = context
        self.io = QuantaCircIO(context)
        self.router = CommandRouter()
        self.session = SessionState()
        self.session.aggregate_context() # Populate git and env context
        self.session.save()
        self.conversation_renderables = []
        self.layout = self.make_layout()

    def make_layout(self) -> Layout:
        """Defines the Rich layout for the CLI."""
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", size=3),
            Layout(ratio=1, name="main"),
            Layout(size=1, name="footer"),
        )
        layout["header"].update(self.get_header_panel())
        layout["main"].update(Panel(Group(*self.conversation_renderables), title="Conversation"))
        layout["footer"].update(self.get_footer_text())
        return layout

    def get_header_panel(self) -> Panel:
        return Panel(
            f"Session ID: {self.session.session_id}",
            title="[quantum]QuantaCirc Conversational Interface[/quantum]",
            border_style="blue"
        )

    def get_footer_text(self) -> Text:
        """Returns the footer text with current energy and Lyapunov state."""
        qc_state = self.session.qc_state
        return Text.from_markup(
            f"[bold]Energy E(S):[/bold] [energy]{qc_state.energy:.4f}[/energy] | "
            f"[bold]Lyapunov Φ(S):[/bold] [lyapunov]{qc_state.lyapunov_potential:.4f}[/lyapunov] | "
            f"[bold]Phase:[/bold] {qc_state.optimization_phase}",
            justify="center"
        )

    async def run_loop(self):
        """The main async conversational loop with a live display."""
        self.io.welcome_screen(self.session) # Show initial welcome

        with Live(self.layout, screen=True, redirect_stderr=False, refresh_per_second=10) as live:
            try:
                while True:
                    self.layout["footer"].update(self.get_footer_text())
                    live.update(self.layout)

                    try:
                        # Pass the footer function to the input prompt's toolbar
                        user_input = await asyncio.to_thread(
                            self.io.get_user_input,
                            self.session,
                            bottom_toolbar=lambda: self.get_footer_text().markup
                        )
                    except (ValueError, EOFError):
                        break

                    if user_input.lower() in ["exit", "quit"]:
                        break

                    # Add user input to conversation display
                    self.conversation_renderables.append(Panel(user_input, title="User", border_style="green"))
                    self.layout["main"].update(Panel(Group(*self.conversation_renderables), title="Conversation"))
                    live.update(self.layout)

                    await self.process_command(user_input, live)
                    self.session.save()

            except KeyboardInterrupt:
                pass
            finally:
                live.stop()
                self.io.goodbye_screen(self.session)
                self.session.save()

    async def process_command(self, user_input: str, live: Live):
        """Processes a single user command, updating and displaying the state."""
        try:
            # --- Handle special commands like 'resolve' ---
            if user_input.strip().startswith("resolve "):
                parts = user_input.strip().split(" ", 1)
                if len(parts) == 2:
                    obligation_id = parts[1]
                    # This is a simplification. In a real system, we'd need to match
                    # a short ID to the full obligation string. For now, we'll require
                    # the user to enter the first part of the obligation string.

                    found_obligation = None
                    for ob in self.session.qc_state.open_obligations:
                        if ob.startswith(obligation_id):
                            found_obligation = ob
                            break

                    if found_obligation and self.session.resolve_obligation(found_obligation):
                        resolved_panel = Panel(f"[green]Obligation resolved:[/green]\n{found_obligation}", title="System Action")
                        self.conversation_renderables.append(resolved_panel)
                    else:
                        error_panel = Panel(f"[red]Could not find or resolve obligation starting with:[/red]\n{obligation_id}", title="Error")
                        self.conversation_renderables.append(error_panel)
                    live.update(self.layout)
                    return # Skip the rest of the NLP pipeline for this command

            # --- Main NLP/Physics Pipeline for standard commands ---
            processing_results = None
            async with self.io.spinner("Processing intent..."):
                processing_results = self.router.process_input(user_input, self.session)

            if not processing_results:
                return

            # --- Update mathematical state ---
            old_lyapunov = self.session.qc_state.lyapunov_potential

            canonical_ast = processing_results["canonical_ast"]
            rho, h_matrix, features = software_to_quantum_functor(canonical_ast)
            new_energy = np.trace(np.matmul(h_matrix, rho)).real
            new_lyapunov = calculate_lyapunov_potential(features, features / 2)

            # --- Mathematical State Enforcement ---
            warnings = []
            # 1. Lyapunov Check
            if new_lyapunov >= old_lyapunov and self.session.history: # Don't check on first command
                warnings.append(
                    f"Lyapunov potential did not decrease (Φ_t-1={old_lyapunov:.4f}, Φ_t={new_lyapunov:.4f}). System may be diverging."
                )

            # 2. Contraction Factor Check (simulated)
            if any(keyword in user_input for keyword in ["fix", "refactor", "optimize"]):
                self.session.qc_state.optimization_phase = "Phase B (Contraction)"
                # Mock a successful contraction for the purpose of the check
                self.session.qc_state.contraction_factor = 0.8
            else:
                self.session.qc_state.optimization_phase = "Phase A (Exploration)"
                self.session.qc_state.contraction_factor = 1.0

            if self.session.qc_state.optimization_phase.startswith("Phase B") and self.session.qc_state.contraction_factor >= 1.0:
                warnings.append(
                    f"Contraction factor λ ({self.session.qc_state.contraction_factor:.2f}) is not < 1 during Phase B."
                )

            # Update session state
            self.session.qc_state.energy = new_energy
            self.session.qc_state.lyapunov_potential = new_lyapunov
            self.session.qc_state.quantum_state = QuantumState(
                density_matrix=rho.tolist(),
                state_vector=[]
            )

            # --- Display results ---
            result_panels = self.render_processing_results(processing_results, warnings)
            self.conversation_renderables.append(Panel(result_panels, title="System", border_style="blue"))
            self.layout["main"].update(Panel(Group(*self.conversation_renderables), title="Conversation"))

            # Add agent response to history for persistence
            self.session.add_history(
                "agent",
                "Agent processed user command.",
                metadata={"processing_results": processing_results}
            )

            live.update(self.layout)

        except ValueError as e:
            self.io.display_error("QCE-CLI-004", str(e), ["Try rephrasing your request."])

    def render_processing_results(self, processing_results: dict, warnings: list) -> Group:
        """Renders the results of the intent processing pipeline into a group of panels."""
        bleu_score = self.session.history[-1].metadata.get('bleu_score', 0.0)

        panels = []
        if warnings:
            warnings_panel = Panel(
                "\n".join(f"- {w}" for w in warnings),
                title="[bold yellow]State Enforcement Warnings[/bold yellow]",
                border_style="yellow"
            )
            panels.append(warnings_panel)

        cnl_panel = Panel(
            f"[bold]CNL Translation:[/bold]\n{processing_results['cnl_translation']}\n\n"
            f"[bold]BLEU Score:[/bold] {bleu_score:.2f}",
            title="[cyan]1. NLP[/cyan]", border_style="cyan"
        )

        intent_panel = Panel(
            f"[bold]DSL:[/bold]\n{str(processing_results['dsl'])}",
            title="[magenta]2. Intent Extraction[/magenta]", border_style="magenta"
        )

        plan_table = self.io.display_plan(processing_results['task_quanta'])

        obligations_panel = Panel(
            "\n".join(f"- {o}" for o in processing_results['delta_closure_obligations']),
            title="[yellow]3. Δ-Closure Obligations[/yellow]", border_style="yellow"
        )

        state_table = self.io.display_results(self.session)

        context_panel = Panel(
            Text(json.dumps(self.session.context, indent=2)),
            title="[bold blue]Session Context[/bold blue]",
            border_style="blue"
        )

        panels.extend([cnl_panel, intent_panel, plan_table, obligations_panel, state_table, context_panel])
        return Group(*panels)


@app.command(name="start")
def main(ctx: typer.Context):
    """
    Initiates an interactive chat session to define and execute tasks.
    """
    cli = ConversationalCLI(context=ctx.obj)
    asyncio.run(cli.run_loop())
