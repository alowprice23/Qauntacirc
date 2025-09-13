import typer
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import Optional
import asyncio

# from core.data_models import AppContext
from demos.scenarios import DEMO_SCENARIOS
from demos.runner import DemoRunner
# from artifacts.generator import ArtifactGenerator

app = typer.Typer()

@app.command("list")
def list_demos():
    """List available demonstration scenarios"""
    from rich.console import Console
    console = Console()

    demo_table = Table(title="Available Demonstrations")
    demo_table.add_column("Name", style="cyan")
    demo_table.add_column("Description", style="white")
    demo_table.add_column("Duration", style="yellow")
    demo_table.add_column("Agents", style="magenta")

    for name, config in DEMO_SCENARIOS.items():
        demo_table.add_row(
            name,
            config["description"],
            config["estimated_duration"],
            ", ".join(config["agents_used"])
        )

    console.print(demo_table)

@app.command()
def run(
    ctx: typer.Context,
    scenario: str = typer.Argument(..., help="Demonstration scenario name"),
    interactive: bool = typer.Option(
        True,
        "--interactive/--automated",
        help="Run in interactive mode with explanations"
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Directory for demo outputs"
    )
):
    """
    Run a specific demonstration scenario.

    Demonstrates QuantaCirc capabilities through concrete examples
    showcasing agent collaboration, formal verification, and
    quantum-mechanical software engineering principles.
    """
    from rich.console import Console
    console = Console()
    # app_context: AppContext = ctx.obj
    # console = app_context.console

    if scenario not in DEMO_SCENARIOS:
        console.print(f"[error]Unknown scenario: {scenario}[/error]")
        console.print("Use 'qc demo list' to see available scenarios")
        raise typer.Exit(1)

    scenario_config = DEMO_SCENARIOS[scenario]

    if output_dir is None:
        output_dir = Path.cwd() / f"demo_{scenario}"

    console.print(f"[bold]🎭 Running Demo: {scenario}[/bold]")
    console.print(f"[cyan]{scenario_config['description']}[/cyan]\n")

    if interactive:
        console.print(Panel(
            scenario_config["overview"],
            title="Demo Overview",
            border_style="blue"
        ))

        if not typer.confirm("Proceed with demonstration?"):
            console.print("[warning]Demo cancelled[/warning]")
            raise typer.Exit(0)

    # Initialize demo runner
    # runner = DemoRunner(scenario_config, app_context.config)
    runner = DemoRunner(scenario_config, {}) # Mocked app_context.config

    try:
        result = asyncio.run(runner.execute(
            output_dir=output_dir,
            interactive=interactive
        ))

        console.print(f"\n[success]✅ Demo completed successfully![/success]")
        console.print(f"Results available in: {output_dir}")

        if result.metrics:
            display_demo_metrics(console, result.metrics)

    except Exception as e:
        console.print(f"[error]Demo failed: {str(e)}[/error]")
        raise typer.Exit(1)

def display_demo_metrics(console, metrics):
    """Display demonstration performance metrics"""
    metrics_table = Table(title="Demo Performance Metrics")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="white")

    for key, value in metrics.items():
        metrics_table.add_row(key, str(value))

    console.print(metrics_table)
