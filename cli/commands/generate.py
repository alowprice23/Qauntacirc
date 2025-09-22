import typer
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from typing import Optional, List
import asyncio

from core.types import AppContext, AgentTask, GenerationRequest, QuantaCircConfig
from core.orchestrator import Orchestrator as AgentOrchestrator
from agents.planck_forge.agent import PlanckForgeAgent
from monitoring.metrics import generation_counter, generation_duration
from core.energy_calculator import EnergyCalculator
from core.lyapunov_monitor import LyapunovMonitor
from core.closure_validator import ClosureValidator
from core.closure_rules import ClosureRuleEngine
from communication.protocol import AgentCommunicationProtocol
from memory.constellation import ConstellationMemory
from memory.types import ConstellationConfig

app = typer.Typer()

async def _requirement_async_logic(
    ctx: typer.Context,
    requirement: str,
    interactive: bool,
    dry_run: bool,
    agent_filter: Optional[List[str]],
    verification_level: str
):
    from rich.console import Console
    console = Console()

    config = QuantaCircConfig()
    app_context = AppContext(
        config=config,
        console=console,
        interactive=interactive,
        log_level="INFO"
    )

    # Increment generation counter
    generation_counter.inc()

    with generation_duration.time():
        # Parse and validate requirement
        console.print(f"[quantum]🔬 Processing requirement:[/quantum] {requirement}")

        # Initialize orchestrator dependencies
        energy_calc = EnergyCalculator(alpha=0.25, beta=0.25, gamma=0.25, delta=0.25)
        lyapunov_monitor = LyapunovMonitor(kappa=1.0, xi=1.0)
        closure_validator = ClosureValidator()

        default_config = ConstellationConfig(
            neo4j_uri="bolt://localhost:7687",
            embedding_dimension=128,
            database_path="/tmp/constellation.db"
        )
        constellation_memory = ConstellationMemory(config=default_config)
        closure_rule_engine = ClosureRuleEngine(memory=constellation_memory)

        comm_protocol = AgentCommunicationProtocol()

        orchestrator = AgentOrchestrator(
            agents=[],
            energy_calculator=energy_calc,
            lyapunov_monitor=lyapunov_monitor,
            closure_validator=closure_validator,
            closure_rule_engine=closure_rule_engine,
            communication_protocol=comm_protocol
        )

        # Create generation request
        gen_request = GenerationRequest(
            requirement=requirement,
            interactive=interactive,
            dry_run=dry_run,
            agent_filter=agent_filter,
            verification_level=verification_level
        )

        # Phase 1: Requirement decomposition via PlanckForge
        console.print("\n[bold]Phase 1: Requirement Quantization[/bold]")
        planck_agent = PlanckForgeAgent()

        try:
            task_quanta = await planck_agent.quantize_requirement(
                requirement_text=requirement,
                context=app_context
            )

            if not task_quanta.success or not task_quanta.quanta:
                 console.print(f"[warning]Could not decompose requirement into actionable tasks. The agent reported: {task_quanta.message}[/warning]")
                 raise typer.Exit(1)


            console.print(f"[success]✓[/success] Decomposed into {len(task_quanta.quanta)} task quanta")

            if interactive and not typer.confirm("\nProceed with generation?"):
                console.print("[warning]Generation cancelled by user[/warning]")
                raise typer.Exit(0)

            # Phase 2: Generation via Orchestrator
            console.print("\n[bold]Phase 2: Code Generation[/bold]")
            result = await orchestrator.execute_pipeline(task_quanta, gen_request)

            if result["success"]:
                 console.print(f"\n[success]🎉 Generation completed successfully![/success]")
                 console.print(f"Modified files: {', '.join(result['modified_files'])}")
            else:
                 console.print(f"\n[error]💥 Generation failed.[/error]")
                 raise typer.Exit(1)

        except Exception as e:
            console.print(f"[error]Requirement decomposition failed: {str(e)}[/error]")
            raise typer.Exit(1)


@app.command()
def requirement(
    ctx: typer.Context,
    requirement: str = typer.Argument(..., help="Natural language requirement"),
    interactive: bool = typer.Option(
        False,
        "--interactive/--non-interactive",
        help="Enable interactive mode for clarification"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show planned actions without executing"
    ),
    agent_filter: Optional[List[str]] = typer.Option(
        None,
        "--agents",
        help="Comma-separated list of agents to use"
    ),
    verification_level: str = typer.Option(
        "standard",
        "--verification",
        help="Verification level: minimal, standard, strict"
    )
):
    """
    Main entry point for requirement generation.
    This is a synchronous wrapper that runs the async logic.
    """
    asyncio.run(_requirement_async_logic(
        ctx,
        requirement,
        interactive,
        dry_run,
        agent_filter,
        verification_level
    ))

@app.command()
def status(ctx: typer.Context):
    from rich.console import Console
    console = Console()
    console.print("Showing generation pipeline status...")

@app.command()
def cancel(ctx: typer.Context, job_id: Optional[str] = typer.Option(None, "--job-id", help="ID of the job to cancel")):
    from rich.console import Console
    console = Console()
    console.print(f"Cancelling generation job {job_id}...")
