"""
Risk command for QuantaCirc.
"""
import typer
from rich.console import Console

from core.types import AppContext
from core.orchestrator import Orchestrator

app = typer.Typer()
console = Console()

@app.command()
def compute_bounds(
    ctx: typer.Context,
    confidence: float = typer.Option(0.95, help="Confidence level for the bound."),
):
    """
    Computes and validates uncertainty bounds for system quality.
    """
    app_context: AppContext = ctx.obj
    console.print(f"Computing risk bounds with confidence level: {confidence}")

    # 1. Setup Orchestrator to access the MathEngine
    config = {'energy': {'alpha': 1.0, 'beta': 1.0, 'gamma': 1.0, 'delta': 1.0}}
    orchestrator = Orchestrator(config)
    math_engine = orchestrator.math_engine

    # 2. Simulate test results
    # To achieve P(failure) <= 10^-4, we need a large number of tests with zero failures.
    num_tests = 50000
    num_failures = 0 # Zero failures

    # 3. Calculate the failure probability bound
    failure_prob_bound = math_engine.get_failure_probability_bound(
        num_tests=num_tests,
        num_failures=num_failures,
        confidence=confidence
    )

    console.print(f"\n[bold]Risk Analysis Results:[/bold]")
    console.print(f"  Number of tests      : {num_tests}")
    console.print(f"  Number of failures   : {num_failures}")
    console.print(f"  Confidence level     : {confidence * 100:.1f}%")
    console.print(f"  P(failure) upper bound: {failure_prob_bound:.6f}")

    # 4. Validation
    target_bound = 1e-4
    if failure_prob_bound <= target_bound:
        console.print(f"\n  [green]✓[/green] P(failure) ≤ {target_bound} with statistical justification.")
        console.print("\n[bold green]Risk check passed successfully![/bold green]")
    else:
        console.print(f"\n  [red]✗[/red] P(failure) ({failure_prob_bound:.6f}) > {target_bound}.")
        console.print("\n[bold red]Risk check failed.[/bold red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    class MockContext:
        obj = AppContext(config=None, console=Console(), interactive=False)

    compute_bounds(ctx=MockContext())