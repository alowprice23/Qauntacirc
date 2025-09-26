import typer
from rich.console import Console
from pathlib import Path
from typing import Optional

from proofs.validators import VerificationManager
from proofs.reporting import VerificationReporter
from core.exceptions import QuantaCircError

app = typer.Typer()
console = Console()

@app.command(name="check-all")
def check_all(
    ctx: typer.Context,
    obligation_file: Path = typer.Argument(..., help="Path to the proof obligation JSON file."),
    generate_proofs: bool = typer.Option(False, "--generate-proofs", help="Attempt to generate proof sketches (not implemented).")
):
    """
    Checks all obligations in a file and reports the status.
    """
    if not obligation_file.exists():
        console.print(f"[bold red]Error: Obligation file not found at {obligation_file}[/bold red]")
        raise typer.Exit(1)

    console.print(f"Checking all proof obligations in [cyan]{obligation_file}[/cyan]...")

    if generate_proofs:
        console.print("[yellow]--generate-proofs is a placeholder and not yet implemented.[/yellow]")

    try:
        manager = VerificationManager()
        results = manager.verify_obligations(str(obligation_file))

        reporter = VerificationReporter(results, str(obligation_file))
        report = reporter.generate_report('text')
        console.print(report)

        if results.get("overall_status") == "failed":
            console.print("\n[bold red]Verification checks failed.[/bold red]")
            raise typer.Exit(1)
        else:
            console.print("\n[bold green]All verification checks passed.[/bold green]")

    except QuantaCircError as e:
        console.print(f"[bold red]An error occurred: {e.message}[/bold red]")
        if e.suggested_fix:
            console.print(f"[yellow]Suggestion: {e.suggested_fix}[/yellow]")
        raise typer.Exit(1)

@app.command(name="smt")
def check_smt(
    ctx: typer.Context,
    property: str = typer.Option(..., "--property", help="The SMT property to check, e.g., 'x > 5'"),
):
    """
    Checks a specific SMT property.
    """
    from core.constraint_solver import SMTConstraintSolver
    console.print(f"Checking SMT property: [bold cyan]'{property}'[/bold cyan]")

    try:
        solver = SMTConstraintSolver()
        # For this standalone check, we assume some context or declare variables.
        # This is a simplified example.
        solver.declare_variable('x', 'Int')
        solver.declare_variable('y', 'Int')

        # Add some base constraints for context
        solver.add_constraint("x < 100")
        solver.add_constraint("y > 0")

        if solver.check_property(property):
            console.print(f"[bold green]Property '{property}' is formally verified.[/bold green]")
        else:
            console.print(f"[bold red]Property '{property}' could not be verified.[/bold red]")
            raise typer.Exit(1)
    except QuantaCircError as e:
        console.print(f"[bold red]SMT solver error: {e.message}[/bold red]")
        raise typer.Exit(1)


@app.command(name="coverage")
def check_coverage(
    ctx: typer.Context,
    obligation_file: Path = typer.Argument(..., help="Path to the proof obligation JSON file."),
    report: bool = typer.Option(False, "--report", help="Generate a detailed coverage report."),
    threshold: Optional[float] = typer.Option(None, "--threshold", help="Fail if coverage is below this percentage (e.g., 80.0).")
):
    """
    Calculates and reports the verification coverage.
    """
    if not obligation_file.exists():
        console.print(f"[bold red]Error: Obligation file not found at {obligation_file}[/bold red]")
        raise typer.Exit(1)

    if not report:
        console.print("[yellow]--report flag not provided. Calculating coverage without generating a report.[/yellow]")

    try:
        # We need to generate a report object to calculate coverage
        reporter = VerificationReporter({}, str(obligation_file))

        obligations = reporter.obligations_data.get("obligations", [])
        total = len(obligations)
        proved = sum(1 for ob in obligations if ob.get("status") == "proved")
        coverage = (proved / total) * 100 if total > 0 else 0

        console.print(f"Verification Coverage: [bold green]{coverage:.2f}%[/bold green] ({proved}/{total} obligations proved)")

        if report:
            console.print("\n--- Full Report ---")
            full_report = reporter.generate_report('text')
            console.print(full_report)

        if threshold is not None:
            console.print(f"Checking against threshold: {threshold:.2f}%")
            if coverage < threshold:
                console.print(f"[bold red]Coverage ({coverage:.2f}%) is below the required threshold ({threshold:.2f}%).[/bold red]")
                raise typer.Exit(1)
            else:
                console.print("[bold green]Coverage meets or exceeds the threshold.[/bold green]")

    except QuantaCircError as e:
        console.print(f"[bold red]An error occurred: {e.message}[/bold red]")
        raise typer.Exit(1)