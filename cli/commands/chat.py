import asyncio
import typer
from rich.console import Console

from cli.bridge import CLIBridge
from cli.state import ConversationState
from core.types import AppContext

app = typer.Typer()

@app.command("chat", help="Start an interactive chat session with the agent orchestrator.")
def chat_session(ctx: typer.Context):
    """
    Initiates a real-time, interactive conversation with the QuantaCirc system.

    This command opens a session where you can send natural language commands
    to the agent orchestrator and receive status updates and results.
    """
    app_context: AppContext = ctx.obj
    console: Console = app_context.console
    state = ConversationState()

    console.print("[bold green]Starting interactive chat session...[/bold green]")
    console.print(f"[dim]Session ID: {state.conversation_id}[/dim]")
    console.print("Type 'exit' or 'quit' to end the session.")

    async def run_chat():
        async with CLIBridge(app_context.config, console) as bridge:
            # The bridge's subscriber will print status updates to the console.
            # Here we focus on sending the user's intents.
            while True:
                try:
                    prompt = await asyncio.to_thread(console.input, "[bold cyan]> [/bold cyan]")
                    if prompt.lower() in ["exit", "quit"]:
                        break

                    if not prompt.strip():
                        continue

                    state.add_user_message(prompt)
                    await bridge.send_intent(prompt, conversation_id=state.conversation_id)

                except (KeyboardInterrupt, EOFError):
                    break

        console.print("\n[bold green]Chat session ended.[/bold green]")

    try:
        asyncio.run(run_chat())
    except Exception as e:
        console.print(f"[bold red]An error occurred during the chat session: {e}[/bold red]")

if __name__ == "__main__":
    # This part is for direct execution testing and would need more robust mocking
    # to function correctly with the new changes.
    pass