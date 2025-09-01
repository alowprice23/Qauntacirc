import typer
from typing_extensions import Annotated
from typing import Optional

# placeholder for version from version.py
__version__ = "0.1.0"

app = typer.Typer(
    name="qc",
    help="QuantaCirc: Agentic CLI for Physics-Grounded Software Engineering",
    add_completion=False,
)

def version_callback(value: bool):
    """Prints the version of the CLI and exits."""
    if value:
        print(f"QuantaCirc CLI Version: {__version__}")
        raise typer.Exit()

@app.command()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
):
    """
    Welcome to the QuantaCirc Agentic CLI.
    
    This is the foundational seed. Run 'qc chat' to start a session.
    """
    print("Welcome to QuantaCirc Seed-Core!")
    print("Run with the 'chat' command to start a session with the agent.")


if __name__ == "__main__":
    app()
