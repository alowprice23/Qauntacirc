import asyncio
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

import nats

from core.orchestrator import Orchestrator
from core.system_state import SystemState
from core.failure_manager import RecoveryStrategy

# Import all agent classes
from agents.planck_forge.agent import PlanckForgeAgent
from agents.schrodinger_dev.agent import SchrodingerDevAgent
from agents.pauli_guard.agent import PauliGuardAgent
from agents.uncertain_ai.agent import UncertainAIAgent
from agents.bose_boost.agent import BoseBoostAgent
from agents.fluctua_test.agent import FluctuaTestAgent as FluctuaTestAgent1
from agents.fluctuatest.agent import FluctuaTestAgent as FluctuaTestAgent2
from agents.hydro_spread.agent import HydroSpreadAgent as HydroSpreadAgent1
from agents.hydrospread.agent import HydroSpreadAgent as HydroSpreadAgent2
from agents.london_link.agent import LondonLinkAgent

app = typer.Typer()
console = Console()

def setup_orchestrator(config: dict) -> Orchestrator:
    """Helper to set up the orchestrator and register all agents."""
    loop = asyncio.get_event_loop()
    nats_client = loop.run_until_complete(nats.connect(servers=["nats://localhost:4222"]))

    orchestrator = Orchestrator(config, nats_client)

    # Register all 10 agents with their dependencies
    orchestrator.register_agent(PlanckForgeAgent(), {"outputs": ["quantized_tasks"]})
    orchestrator.register_agent(SchrodingerDevAgent(), {"inputs": ["quantized_tasks"], "outputs": ["generated_code"]})
    orchestrator.register_agent(PauliGuardAgent(), {"inputs": ["generated_code"], "outputs": ["deduplicated_code"]})
    orchestrator.register_agent(UncertainAIAgent(), {"inputs": ["deduplicated_code"], "outputs": ["generated_tests"]})
    orchestrator.register_agent(BoseBoostAgent(), {"inputs": ["deduplicated_code"], "outputs": ["optimized_code"]})
    orchestrator.register_agent(FluctuaTestAgent1(), {"inputs": ["generated_tests", "optimized_code"], "outputs": ["test_results"]})
    orchestrator.register_agent(FluctuaTestAgent2(), {"inputs": ["generated_tests", "optimized_code"], "outputs": ["chaos_test_results"]})
    orchestrator.register_agent(HydroSpreadAgent1(), {"inputs": ["optimized_code"], "outputs": ["generated_docs"]})
    orchestrator.register_agent(HydroSpreadAgent2(), {"inputs": ["optimized_code", "test_results"], "outputs": ["deployment_status"]})
    orchestrator.register_agent(LondonLinkAgent(), {"inputs": ["optimized_code"], "outputs": ["dependency_list"]})

    return orchestrator

@app.command(name="run", help="Run the full orchestration pipeline.")
def run_orchestrator(
    task: str = typer.Argument(..., help="The main task for the orchestrator to execute."),
    parallel: bool = typer.Option(False, "--parallel", help="Enable parallel execution of agents."),
    max_agents: int = typer.Option(4, "--max-agents", help="Maximum number of parallel agents."),
    simulate_failure: Optional[str] = typer.Option(None, "--simulate-failure", help="Simulate failure for a specific agent."),
    recovery_strategy: RecoveryStrategy = typer.Option(RecoveryStrategy.CONTINUE.value, "--recovery-strategy", help="Recovery strategy for failures."),
    cpu_limit: Optional[float] = typer.Option(None, "--cpu-limit", help="CPU usage limit in percent."),
    memory_limit: Optional[float] = typer.Option(None, "--memory-limit", help="Memory usage limit in percent."),
    monitor: bool = typer.Option(False, "--monitor", help="Monitor resource usage during the run.")
):
    """
    Runs the agent orchestration system with various configurations.
    """
    config = {
        "resource_limits": {
            "cpu": cpu_limit,
            "memory": memory_limit,
        }
    }
    orchestrator = setup_orchestrator(config)
    initial_state = SystemState()

    console.print(f"[bold green]Starting orchestrator run for task: '{task}'[/bold green]")

    loop = asyncio.get_event_loop()
    final_state = loop.run_until_complete(orchestrator.run(
        initial_state=initial_state,
        task=task,
        max_agents=max_agents if parallel else 1,
        recovery_strategy=recovery_strategy,
        simulate_failure=simulate_failure
    ))

    console.print("[bold green]Orchestrator run finished.[/bold green]")
    console.print("Final state:")
    console.print(final_state.data)

    if monitor:
        console.print("\n[bold yellow]Resource Usage Metrics:[/bold yellow]")
        usage = orchestrator.resource_manager.get_current_usage()
        console.print(f"  CPU Usage: {usage['cpu_percent']:.2f}%")
        console.print(f"  Memory Usage: {usage['memory_percent']:.2f}%")

    console.print("\n[bold yellow]Execution Metrics:[/bold yellow]")
    metrics = orchestrator.metrics_manager.get_metrics()
    table = Table(title="Orchestration Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    for k, v in metrics['counters'].items():
        table.add_row(k, str(v))
    for k, v in metrics['histograms'].items():
        table.add_row(f"{k} (avg_duration)", f"{v['sum'] / v['count']:.4f}s")
    console.print(table)


@app.command(name="dry-run", help="Show the execution plan without running agents.")
def dry_run(
    show_dependencies: bool = typer.Option(False, "--show-dependencies", help="Display agent dependencies.")
):
    """
    Performs a dry run, resolving dependencies and showing the execution plan.
    """
    orchestrator = setup_orchestrator({})

    console.print("[bold green]Orchestrator Dry Run[/bold green]")

    if show_dependencies:
        console.print("\n[bold yellow]Agent Dependencies:[/bold yellow]")
        table = Table(title="Agent Dependencies")
        table.add_column("Agent", style="cyan")
        table.add_column("Inputs", style="magenta")
        table.add_column("Outputs", style="green")
        for name, deps in orchestrator.agent_dependencies.items():
            table.add_row(name, str(deps.get('inputs', [])), str(deps.get('outputs', [])))
        console.print(table)

    try:
        execution_plan = orchestrator.dependency_graph.resolve_dependencies()
        console.print("\n[bold yellow]Execution Plan:[/bold yellow]")
        for i, agent_name in enumerate(execution_plan):
            console.print(f"  {i+1}. {agent_name}")
    except Exception as e:
        console.print(f"[bold red]Error resolving dependencies: {e}[/bold red]")