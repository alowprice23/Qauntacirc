"""
Optimize command for QuantaCirc.
"""
import typer
from rich.console import Console
import numpy as np
import time

from core.types import AppContext, QCState, SoftwareState, EnergyComponents
from core.orchestrator import Orchestrator

app = typer.Typer()
console = Console()

@app.command()
def run(
    ctx: typer.Context,
    max_iterations: int = typer.Option(100, help="Maximum number of optimization iterations."),
    log_phases: bool = typer.Option(False, help="Log phase transitions during optimization."),
):
    """
    Runs the two-phase annealer to optimize the system's energy.
    """
    app_context: AppContext = ctx.obj
    console.print(f"Running two-phase annealer for {max_iterations} iterations...")

    # 1. Setup initial state and orchestrator
    mock_state = QCState(
        software_state=SoftwareState(component_versions={}, config_hashes={}),
        modules=["def main():\n  print('hello')"],
        dependency_graph=np.array([[0]]),
    )

    config = {
        'energy': {'alpha': 1.0, 'beta': 1.0, 'gamma': 1.0, 'delta': 1.0},
        'annealing': {
            "initial_temp": 100.0, "phase_b_start_temp": 10.0, "min_temp": 0.01,
            "phase_switch_variance_threshold": 10.0, # Loosen for simulation
            "phase_switch_gradient_threshold": 0.5, # Loosen for simulation
        },
        'lyapunov': {}, 'convergence': {}
    }
    orchestrator = Orchestrator(config)

    # Set initial energy
    total_energy, components = orchestrator.math_engine.compute_system_energy(mock_state)
    mock_state.energy = total_energy
    mock_state.energy_components = EnergyComponents(**components)

    # 2. Run the optimization
    final_state = orchestrator.run_optimization(mock_state, max_iterations)

    # 3. Final Validation
    annealer = orchestrator.annealer
    console.print("\n[bold]Validation Checks:[/bold]")
    if "B" in annealer.phase:
        console.print("  [green]✓[/green] Phase B was reached.")
    else:
        console.print("  [red]✗[/red] Phase B was not reached.")

    if annealer.contraction_factor_history and annealer.contraction_factor_history[0] < 1.0:
        console.print(f"  [green]✓[/green] Contraction factor λ ({annealer.contraction_factor_history[0]:.2f}) < 1 in Phase B.")
    elif "B" in annealer.phase:
        console.print("  [red]✗[/red] Contraction factor not measured or not < 1 in Phase B.")

    if "B" in annealer.phase and annealer.contraction_factor_history and annealer.contraction_factor_history[0] < 1.0:
        console.print("\n[bold green]Optimize check passed successfully![/bold green]")
    else:
        console.print("\n[bold red]Optimize check failed.[/bold red]")
        raise typer.Exit(code=1)