import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from typing import Optional
import shutil
import yaml

from templates.project import PROJECT_TEMPLATES
from core.types import AppContext, QuantaCircConfig

app = typer.Typer()

@app.command()
def create(
    ctx: typer.Context,
    project_name: str = typer.Argument(..., help="Name of the new project"),
    template: str = typer.Option(
        "default",
        "--template",
        "-t",
        help="Project template to use"
    ),
    target_dir: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Target directory (defaults to current)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing directory"
    )
):
    from rich.console import Console
    console = Console()

    if "/" in project_name or "\\" in project_name:
        console.print("[error]Project name cannot contain path separators.[/error]")
        raise typer.Exit(1)

    # Determine project directory
    if target_dir is None:
        target_dir = Path.cwd()
    project_path = target_dir / project_name

    # Check for existing directory
    if project_path.exists() and not force:
        console.print(f"[error]Project directory already exists: {project_path}[/error]")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)

    # Validate template
    if template not in PROJECT_TEMPLATES:
        console.print(f"[error]Unknown template: {template}[/error]")
        console.print(f"Available templates: {', '.join(PROJECT_TEMPLATES.keys())}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Create project structure
        task1 = progress.add_task("Creating project structure...", total=None)
        if force and project_path.exists():
            shutil.rmtree(project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        # Generate from template
        template_config = PROJECT_TEMPLATES[template]

        progress.update(task1, description="Generating project files...")

        # Initialize quantum state
        progress.update(task1, description="Initializing quantum state...")

        # Create configuration file
        progress.update(task1, description="Writing configuration...")
        config_data = {
            "project": {
                "name": project_name,
                "template": template,
                "version": "0.1.0"
            },
            "quantum": {
                "convergence_threshold": 1e-6,
                "annealing_schedule": "adaptive"
            },
            "agents": {
                "enabled": list(template_config.get("agents", [])),
                "prompt_version": "v1.0"
            }
        }

        with open(project_path / "quantacirc.yml", "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)

        progress.remove_task(task1)

    console.print(f"[success]✓[/success] Project '{project_name}' created successfully")
    console.print(f"[quantum]📁[/quantum] Location: {project_path}")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  cd {project_name}")
    console.print("  qc status")
    console.print("  qc generate 'your first requirement'")

@app.command("list-templates")
def list_templates():
    """List available project templates"""
    from rich.console import Console
    console = Console()
    console.print("[bold]Available Templates:[/bold]\n")

    for name, config in PROJECT_TEMPLATES.items():
        console.print(f"[quantum]{name}[/quantum]")
        console.print(f"  {config.get('description', 'No description')}")
        console.print(f"  Agents: {', '.join(config.get('agents', []))}")
        console.print()
