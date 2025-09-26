"""
Debug command for QuantaCirc.
"""
import typer
from rich.console import Console
import numpy as np

from core.types import AppContext, QCState, SoftwareState, EnergyComponents
from core.orchestrator import Orchestrator
from math_utils.dim_analysis import setup_quantacirc_analyzer, validate_energy_equation

app = typer.Typer()
console = Console()

@app.command()
def energy_breakdown(
    ctx: typer.Context,
    project: str = typer.Option("test-api", help="Project name to debug"),
):
    """
    Performs a debug check on the energy calculation, showing a breakdown
    of the components.
    """
    app_context: AppContext = ctx.obj
    console.print(f"Running energy breakdown for project: [bold cyan]{project}[/bold cyan]")

    # 1. Create a mock QCState for the test-api project
    mock_state = QCState(
        software_state=SoftwareState(component_versions={}, config_hashes={}),
        modules=[
            "def main():\n  print('hello')",
            "import os\n\nclass Helper:\n  pass"
        ],
        dependency_graph=np.array([[0, 1], [0, 0]]), # Module 0 depends on module 1
        constraints=[
            {'name': 'max_complexity', 'value': 2.5, 'weight': 1.0},
            {'name': 'min_coverage', 'value': -0.2, 'weight': 2.0} # Negative value means constraint is met
        ],
        modules_metadata=[
            {'debt_score': 15, 'days_since_refactor': 10},
            {'debt_score': 5, 'days_since_refactor': 120}
        ]
    )

    # 2. Initialize the Orchestrator
    engine_config = {
        'energy': {'alpha': 1.0, 'beta': 1.0, 'gamma': 1.0, 'delta': 1.0},
        'annealing': {}, 'lyapunov': {}, 'convergence': {}
    }
    orchestrator = Orchestrator(engine_config)

    # 3. Calculate energy using the orchestrator's math engine
    total_energy, components = orchestrator.math_engine.compute_system_energy(mock_state)
    mock_state.energy = total_energy
    mock_state.energy_components = EnergyComponents(**components)

    # 4. Print the breakdown
    console.print("\n[bold green]Energy Component Breakdown:[/bold green]")
    console.print(f"  Complexity : {components['complexity']:.4f}")
    console.print(f"  Coupling   : {components['coupling']:.4f}")
    console.print(f"  Constraints: {components['constraints']:.4f}")
    console.print(f"  Debt       : {components['debt']:.4f}")
    console.print("---------------------------")
    console.print(f"  [bold]Total Energy: {total_energy:.4f}[/bold]")

    # 5. Validation Test
    console.print("\n[bold]Validation Checks:[/bold]")
    sum_of_components = sum(components.values())
    dim_analyzer = setup_quantacirc_analyzer()
    is_homogeneous = validate_energy_equation(dim_analyzer)

    if abs(total_energy - sum_of_components) < 1e-9:
        console.print("  [green]✓[/green] Energy components sum correctly.")
    else:
        console.print(f"  [red]✗[/red] Sum of components ({sum_of_components}) does not match total energy ({total_energy}).")

    all_positive = all(v >= 0 for v in components.values())
    if all_positive:
        console.print("  [green]✓[/green] All energy components are positive.")
    else:
        console.print(f"  [red]✗[/red] Some energy components are negative: {components}")

    if is_homogeneous:
        console.print("  [green]✓[/green] Energy equation is dimensionally homogeneous.")
    else:
        console.print("  [red]✗[/red] Energy equation is not dimensionally homogeneous.")


    if abs(total_energy - sum_of_components) < 1e-9 and all_positive and is_homogeneous:
        console.print("\n[bold green]Debug check passed successfully![/bold green]")
    else:
        console.print("\n[bold red]Debug check failed.[/bold red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    # This allows running the command directly for testing
    # You would need to mock the typer context object
    class MockContext:
        obj = AppContext(config=QuantaCircConfig(), console=Console(), interactive=False)

    energy_breakdown(ctx=MockContext())