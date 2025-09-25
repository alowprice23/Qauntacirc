import asyncio
import typer
from rich.console import Console

from cli.bridge import CLIBridge
from core.types import AppContext

app = typer.Typer()

@app.command("self-test", help="Run a self-test of the QuantaCirc system.")
def self_test(
    ctx: typer.Context,
    agents: bool = typer.Option(
        False,
        "--agents",
        help="Test the status of all registered agents."
    )
):
    """
    Performs diagnostic checks on the system components.
    """
    app_context: AppContext = ctx.obj
    console: Console = app_context.console

    if not agents:
        console.print("[yellow]Please specify a component to test, e.g., --agents.[/yellow]")
        raise typer.Exit()

    async def run_agent_test():
        console.print("[bold blue]Connecting to messaging system to check for agent heartbeats...[/bold blue]")

        # This is a placeholder. A full implementation would involve a request-reply
        # with the orchestrator or listening for agent heartbeats.
        async with CLIBridge(app_context.config, console) as bridge:
            if bridge.is_connected:
                console.print("[green]Connection to messaging system successful.[/green]")
                console.print("[yellow]Agent status check not fully implemented. Listening for status messages for 5 seconds...[/yellow]")
                # The bridge's subscriber will print any messages it receives.
                await asyncio.sleep(5)
                console.print("[bold blue]Self-test finished.[/bold blue]")
            else:
                console.print("[red]Failed to connect to messaging system.[/red]")
                raise typer.Exit(1)

    if agents:
        try:
            asyncio.run(run_agent_test())
        except Exception as e:
            console.print(f"[bold red]An error occurred during the self-test: {e}[/bold red]")
            raise typer.Exit(1)