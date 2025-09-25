import asyncio
import sys
import typer
from rich.console import Console

from cli.bridge import CLIBridge
from core.types import AppContext

app = typer.Typer()

@app.command("process", help="Process a single intent in batch mode.")
def process_intent(
    ctx: typer.Context,
    batch: bool = typer.Option(
        False,
        "--batch",
        help="Read intent from standard input for batch processing."
    ),
    intent: str = typer.Argument(
        None,
        help="The intent to process. If not provided, reads from stdin."
    )
):
    """
    Processes a single, non-interactive intent.

    This is useful for scripting and batch operations. The intent can be
    provided as an argument or piped via standard input.
    """
    app_context: AppContext = ctx.obj
    console: Console = app_context.console

    if batch:
        if not sys.stdin.isatty():
            intent_text = sys.stdin.read().strip()
        else:
            console.print("[bold red]Error: --batch flag requires input from stdin.[/bold red]")
            raise typer.Exit(1)
    elif intent:
        intent_text = intent
    else:
        console.print("[bold red]Error: You must provide an intent as an argument or use --batch with stdin.[/bold red]")
        raise typer.Exit(1)

    if not intent_text:
        console.print("[bold yellow]No intent provided. Nothing to do.[/bold yellow]")
        raise typer.Exit()

    async def run_process():
        async with CLIBridge(app_context.config, console) as bridge:
            await bridge.send_intent(intent_text)
            # In a real scenario, we might want to wait for a completion signal.
            # For now, we send and exit. The subscriber will print status updates.
            # Adding a small delay to allow messages to be printed.
            await asyncio.sleep(2)

    try:
        asyncio.run(run_process())
        console.print("[bold green]Intent processed successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]An error occurred while processing the intent: {e}[/bold red]")
        raise typer.Exit(1)