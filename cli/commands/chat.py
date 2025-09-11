import typer
from rich.panel import Panel

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

@app.command(name="start")
def main(ctx: typer.Context):
    """
    Initiates an interactive chat session to define and execute tasks.
    """
    app_context: AppContext = ctx.obj
    io = QuantaCircIO(app_context)
    router = CommandRouter()

    # 1. Initialize session state
    session = SessionState()
    session.save() # Initial save to create the session file

    # 2. Display welcome screen with initial state
    io.welcome_screen(session)

    # 3. Main conversational loop
    try:
        while True:
            # Get user input
            try:
                user_input = io.get_user_input(session)
            except ValueError as e:
                # This handles CNL validation failure in non-interactive mode
                io.display_error("QCE-CLI-003", str(e))
                break

            if user_input.lower() in ["exit", "quit"]:
                break

            # Process input through the router
            try:
                processing_results = router.process_input(user_input)
            except ValueError as e:
                io.display_error("QCE-CLI-004", str(e), ["Try rephrasing your request.", "Be more explicit about the action and subject."])
                continue

            # --- Update mathematical state based on processing ---
            canonical_ast = processing_results["canonical_ast"]

            # 1. Call the core mathematical functor with the AST derived from user intent
            rho, h_matrix, features = software_to_quantum_functor(canonical_ast)

            # 2. Calculate energy: E = Tr(H * rho)
            new_energy = np.trace(np.matmul(h_matrix, rho)).real

            # 3. For Lyapunov, use the features returned by the functor
            new_lyapunov = calculate_lyapunov_potential(features, features / 2) # Mock target state

            # 4. Update the session state
            session.qc_state.energy = new_energy
            session.qc_state.lyapunov_potential = new_lyapunov
            session.qc_state.quantum_state = QuantumState(
                density_matrix=rho.tolist(),
                state_vector=[] # state_vector is not calculated by this functor
            )

            # --- Display all results as required by the prompt ---

            bleu_score = session.history[-1].metadata.get('bleu_score', 0.0)
            cnl_panel = Panel(
                f"[bold]CNL Translation:[/bold]\n{processing_results['cnl_translation']}\n\n"
                f"[bold]BLEU Score:[/bold] {bleu_score:.2f}",
                title="[cyan]1. Natural Language Processing[/cyan]",
                border_style="cyan"
            )
            io.console.print(cnl_panel)

            intent_panel = Panel(
                f"[bold]DSL:[/bold]\n{str(processing_results['dsl'])}\n\n"
                f"[bold]Energy Estimate:[/bold] {new_energy:.4f}\n\n"
                f"[bold]Gallina Spec (mock):[/bold]\n{processing_results['gallina_spec']}",
                title="[magenta]2. Physics-Based Intent Extraction[/magenta]",
                border_style="magenta"
            )
            io.console.print(intent_panel)

            io.display_plan(processing_results['task_quanta'])

            obligations_panel = Panel(
                "\n".join(f"- {o}" for o in processing_results['delta_closure_obligations']),
                title="[yellow]5. Δ-Closure Obligation Set[/yellow]",
                border_style="yellow"
            )
            io.console.print(obligations_panel)

            io.console.print(Panel("[bold]4. Mathematical State Initialization[/bold]", border_style="green"))
            io.display_results(session)

            session.save()

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        io.goodbye_screen(session)
        session.save()
