import typer
from rich.table import Table
from rich.tree import Tree
from rich.json import JSON
from pathlib import Path
from typing import Optional, List
import json

# from core.types import AppContext
from memory.constellation import ConstellationMemory
from memory.query import MemoryQuery, QueryBuilder
from memory.patterns import PatternAnalyzer

app = typer.Typer()

@app.command()
def query(
    ctx: typer.Context,
    search_term: str = typer.Argument(..., help="Search term or query"),
    memory_type: str = typer.Option(
        "all",
        "--type",
        help="Memory type: all, decisions, patterns, context"
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        help="Maximum number of results"
    ),
    format_output: str = typer.Option(
        "table",
        "--format",
        help="Output format: table, json, tree"
    )
):
    """
    Query the Constellation memory system.

    Search through historical decisions, learned patterns, and
    contextual information stored by the QuantaCirc system.
    """
    from rich.console import Console
    console = Console()
    # app_context: AppContext = ctx.obj
    # console = app_context.console

    # Initialize memory system
    # memory = ConstellationMemory(app_context.config)
    memory = ConstellationMemory({}) # Mocked app_context.config
    query_builder = QueryBuilder()

    # Build query
    query = query_builder.search(search_term).type(memory_type).limit(limit).build()

    console.print(f"[quantum]🧠 Searching memory for: '{search_term}'[/quantum]\n")

    try:
        results = memory.query(query)

        if not results:
            console.print("[warning]No results found[/warning]")
            return

        console.print(f"[success]Found {len(results)} results[/success]\n")

        if format_output == "json":
            console.print(JSON.from_data([r.to_dict() for r in results]))
        elif format_output == "tree":
            display_memory_tree(console, results)
        else:
            display_memory_table(console, results)

    except Exception as e:
        console.print(f"[error]Memory query failed: {str(e)}[/error]")
        raise typer.Exit(1)

@app.command()
def patterns(
    ctx: typer.Context,
    analysis_type: str = typer.Option(
        "frequent",
        "--type",
        help="Analysis type: frequent, trending, correlations"
    ),
    time_range: str = typer.Option(
        "7d",
        "--range",
        help="Time range: 1h, 1d, 7d, 30d"
    )
):
    """
    Analyze patterns in the Constellation memory.

    Discover frequently used patterns, trending decisions,
    and correlations in system behavior.
    """
    from rich.console import Console
    console = Console()
    # app_context: AppContext = ctx.obj
    # console = app_context.console

    # memory = ConstellationMemory(app_context.config)
    memory = ConstellationMemory({}) # Mocked app_context.config
    analyzer = PatternAnalyzer(memory)

    console.print(f"[quantum]🔍 Analyzing {analysis_type} patterns over {time_range}[/quantum]\n")

    try:
        patterns = analyzer.analyze(analysis_type, time_range)

        pattern_table = Table(title=f"{analysis_type.title()} Patterns")
        pattern_table.add_column("Pattern", style="cyan")
        pattern_table.add_column("Frequency", style="yellow")
        pattern_table.add_column("Confidence", style="green")
        pattern_table.add_column("Last Seen", style="white")

        for pattern in patterns:
            pattern_table.add_row(
                pattern.description,
                str(pattern.frequency),
                f"{pattern.confidence:.2f}",
                pattern.last_seen.strftime("%Y-%m-%d %H:%M")
            )

        console.print(pattern_table)

    except Exception as e:
        console.print(f"[error]Pattern analysis failed: {str(e)}[/error]")
        raise typer.Exit(1)

@app.command()
def cleanup(
    ctx: typer.Context,
    age_threshold: str = typer.Option(
        "30d",
        "--age",
        help="Delete memories older than threshold"
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Show what would be deleted without actually deleting"
    )
):
    """Clean up old memory entries"""
    from rich.console import Console
    console = Console()
    console.print(f"Cleaning up memories older than {age_threshold}...")
    if dry_run:
        console.print("Dry run, no changes will be made.")

def display_memory_table(console, results):
    """Display memory results in table format"""
    table = Table(title="Memory Search Results")
    table.add_column("Type", style="cyan")
    table.add_column("Timestamp", style="yellow")
    table.add_column("Summary", style="white")
    table.add_column("Relevance", style="green")

    for result in results:
        table.add_row(
            result.type,
            result.timestamp.strftime("%Y-%m-%d %H:%M"),
            result.summary[:60] + "..." if len(result.summary) > 60 else result.summary,
            f"{result.relevance_score:.2f}"
        )

    console.print(table)

def display_memory_tree(console, results):
    """Display memory results in tree format"""
    tree = Tree("Memory Results")

    for result in results:
        branch = tree.add(f"[cyan]{result.type}[/cyan] - {result.timestamp}")
        branch.add(f"Summary: {result.summary}")
        branch.add(f"Relevance: {result.relevance_score:.2f}")

    console.print(tree)
