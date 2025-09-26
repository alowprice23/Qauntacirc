import typer
from typing import Optional
from rich.console import Console

from proofs.validators import VerificationManager
from proofs.reporting import VerificationReporter

app = typer.Typer()
console = Console()

@app.command()
def run(
    ctx: typer.Context,
    agent_name: str = typer.Argument(..., help="Name of the agent to run, e.g., 'schrodinger_dev'"),
    generate: Optional[str] = typer.Option(None, "--generate", help="A description of the task for the agent to perform, e.g., 'user_service'"),
    verify: bool = typer.Option(False, "--verify", help="Run verification checks on the generated output")
):
    """
    Run a specific agent to perform a task like code generation.
    """
    console.print(f"Executing agent: [bold cyan]{agent_name}[/bold cyan]")

    if not generate:
        console.print("[yellow]Warning: No generation task specified. Use --generate.[/yellow]")
        return

    # This is a placeholder for the actual agent execution logic.
    # In a real system, this would trigger the agent and produce files.
    console.print(f"Agent task: Generate [bold]{generate}[/bold]")
    console.print("...Agent running (mocked)...")

    # Mocked output from the agent
    mock_task_id = "task_abc123"
    mock_code_path = f"generated/{mock_task_id}.py"
    mock_obligation_path = f"generated/{mock_task_id}.json"

    # Create dummy generated files for the verification step
    import os
    os.makedirs("generated", exist_ok=True)
    with open(mock_code_path, "w") as f:
        f.write("# Mock generated code\n")
        f.write("def my_func(x, y): return x + y\n")

    with open(mock_obligation_path, "w") as f:
        f.write("""
{
  "version": "1.0",
  "task_id": "task_abc123",
  "file": "task_abc123.py",
  "obligations": [
    {
      "id": "obligation-1",
      "type": "smt",
      "property": "x > 0",
      "description": "Ensure x is positive.",
      "status": "pending"
    },
    {
      "id": "obligation-2",
      "type": "coq",
      "property": "functional correctness",
      "description": "Prove functional correctness.",
      "status": "pending"
    }
  ]
}
        """)

    console.print(f"Mocked agent output created in [green]generated/[/green]")

    if verify:
        console.print("\n[bold]Verifying generated code...[/bold]")
        try:
            # The agent's execution should produce an obligation file.
            manager = VerificationManager()
            results = manager.verify_obligations(mock_obligation_path)

            reporter = VerificationReporter(results, mock_obligation_path)
            report = reporter.generate_report('text')
            console.print(report)

            if results.get("overall_status") == "failed":
                console.print("[bold red]Verification failed.[/bold red]")
                raise typer.Exit(1)
            else:
                console.print("[bold green]Verification successful.[/bold green]")

        except Exception as e:
            console.print(f"[bold red]An error occurred during verification: {e}[/bold red]")
            raise typer.Exit(1)
    else:
        console.print("\n--verify flag not used. Skipping verification.")