import typer
from rich.table import Table
from rich.tree import Tree
from rich.json import JSON
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from core.persistence import PersistenceManager
from memory.constellation import ConstellationMemory
from memory.query import QueryBuilder
from memory.patterns import PatternAnalyzer

app = typer.Typer(help="Interact with the Constellation memory system.")

# --- Global State (for CLI session) ---
# In a real app, this would be managed via a context object (ctx.obj)
try:
    storage_path = Path("./.quantacirc_cli_storage")
    persistence_manager = PersistenceManager(storage_path)
    constellation_memory = ConstellationMemory(persistence_manager=persistence_manager)
except Exception as e:
    print(f"Error initializing memory: {e}")
    constellation_memory = None

# --- Commands ---

@app.command("add-fact")
def add_fact(
    ctx: typer.Context,
    content: str = typer.Argument(..., help="The content of the fact."),
    fact_type: str = typer.Option("observation", "--type", help="The type of fact."),
    access_level: str = typer.Option("private", "--access", help="Access level (private/public)."),
    owner: str = typer.Option("cli_user", "--owner", help="Owner of the fact."),
    timestamp: Optional[str] = typer.Option(None, "--timestamp", help="Timestamp in ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SS)."),
):
    """Adds a new fact to the Constellation memory."""
    from rich.console import Console
    console = Console()
    if not constellation_memory:
        console.print("[error]Memory system not initialized.[/error]")
        raise typer.Exit(1)

    try:
        # This is a bit of a hack for the CLI. In a real system,
        # the ConstellationMemory would handle this more gracefully.
        fact_id = constellation_memory.add_fact(
            content=content, fact_type=fact_type, access_level=access_level, owner=owner
        )
        if timestamp:
            ts_dt = datetime.fromisoformat(timestamp)
            constellation_memory.graph.nodes[fact_id]['timestamp'] = ts_dt

        constellation_memory.persist()
        console.print(f"[success]Successfully added fact with ID: {fact_id}[/success]")
    except Exception as e:
        console.print(f"[error]Failed to add fact: {e}[/error]")
        raise typer.Exit(1)

@app.command("learn-text")
def learn_text(
    ctx: typer.Context,
    text: str = typer.Argument(..., help="The text to learn from."),
    owner: str = typer.Option("cli_user", "--owner", help="Owner of the information."),
):
    """Processes unstructured text to extract facts and relationships."""
    from rich.console import Console
    console = Console()
    if not constellation_memory:
        console.print("[error]Memory system not initialized.[/error]")
        raise typer.Exit(1)

    try:
        constellation_memory.learn_from_artifact(
            artifact_type="unstructured_text",
            content=text,
            owner=owner
        )
        constellation_memory.persist()
        console.print(f"[success]Successfully processed text and updated memory.[/success]")
    except Exception as e:
        console.print(f"[error]Failed to process text: {e}[/error]")
        raise typer.Exit(1)

@app.command()
def query(
    ctx: typer.Context,
    search_term: str = typer.Argument(..., help="Search term or query."),
    limit: int = typer.Option(10, "--limit", help="Maximum number of results."),
    user_id: str = typer.Option("cli_user", "--user", help="User ID for access control."),
    format_output: str = typer.Option("table", "--format", help="Output format: table, json."),
):
    """Queries the Constellation memory for facts and decisions."""
    from rich.console import Console
    console = Console()
    if not constellation_memory:
        console.print("[error]Memory system not initialized.[/error]")
        raise typer.Exit(1)

    query_builder = QueryBuilder()
    built_query = (
        query_builder.search(search_term)
        .limit(limit)
        .as_user(user_id, roles=["user"]) # Assuming default role
        .build()
    )

    console.print(f"[quantum]🧠 Searching memory for: '{search_term}'[/quantum]\n")

    try:
        results = constellation_memory.query(built_query)
        if not results:
            console.print("[warning]No results found[/warning]")
            return

        console.print(f"[success]Found {len(results)} results[/success]\n")
        if format_output == "json":
            serializable_results = []
            for _, data in results:
                if 'timestamp' in data and isinstance(data['timestamp'], datetime):
                    data['timestamp'] = data['timestamp'].isoformat()
                serializable_results.append(data)
            console.print(JSON.from_data(serializable_results))
        else:
            display_memory_table(console, results)
    except Exception as e:
        console.print(f"[error]Memory query failed: {e}[/error]")
        raise typer.Exit(1)


@app.command("analyze-patterns")
def analyze_patterns(
    ctx: typer.Context,
    domain: str = typer.Option(..., "--domain", help="The domain to analyze (e.g., 'authentication')."),
    projects: str = typer.Option("all", "--projects", help="Comma-separated list of projects or 'all'. (Currently not implemented)"),
):
    """Analyzes and identifies common patterns within a domain."""
    from rich.console import Console
    console = Console()
    if not constellation_memory:
        console.print("[error]Memory system not initialized.[/error]")
        raise typer.Exit(1)

    analyzer = PatternAnalyzer(constellation_memory)
    console.print(f"[quantum]🔍 Analyzing patterns for domain '{domain}'[/quantum]\n")

    try:
        patterns = analyzer.analyze("common_relationships", domain=domain)
        if not patterns:
            console.print("[warning]No significant patterns found.[/warning]")
            return

        table = Table(title=f"Common Patterns in '{domain}'")
        table.add_column("Pattern", style="cyan")
        table.add_column("Frequency", style="yellow")
        table.add_column("Confidence", style="green")
        table.add_column("Last Seen", style="white")

        for pattern in patterns:
            table.add_row(
                pattern.description,
                str(pattern.frequency),
                f"{pattern.confidence:.2f}",
                pattern.last_seen.strftime("%Y-%m-%d %H:%M"),
            )
        console.print(table)
    except Exception as e:
        console.print(f"[error]Pattern analysis failed: {e}[/error]")
        raise typer.Exit(1)

@app.command()
def timeline(
    ctx: typer.Context,
    query: str = typer.Option(..., "--query", help="The concept or pattern to track over time (e.g., 'authentication')."),
    span: int = typer.Option(6, "--span", help="The time span in months to look back."),
):
    """Shows the evolution of patterns or concepts over time."""
    from rich.console import Console
    console = Console()
    if not constellation_memory:
        console.print("[error]Memory system not initialized.[/error]")
        raise typer.Exit(1)

    analyzer = PatternAnalyzer(constellation_memory)
    console.print(f"[quantum]⏳ Tracking evolution of '{query}' over the last {span} months[/quantum]\n")

    try:
        timeline_data = analyzer.analyze("evolution", domain=query, time_span_months=span)
        if not timeline_data:
            console.print("[warning]No historical data found for this query.[/warning]")
            return

        tree = Tree(f"Evolution of '{query}'")
        for month, patterns in sorted(timeline_data.items()):
            month_branch = tree.add(f"[yellow]{month}[/yellow]")
            if patterns:
                for pattern in patterns:
                    month_branch.add(f"[cyan]{pattern['description']}[/cyan] (Freq: {pattern['frequency']})")
            else:
                month_branch.add("[dim]No significant patterns[/dim]")
        console.print(tree)
    except Exception as e:
        console.print(f"[error]Timeline analysis failed: {e}[/error]")
        raise typer.Exit(1)

def display_memory_table(console, results):
    """Display memory results in a table format."""
    table = Table(title="Memory Search Results")
    table.add_column("ID", style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Timestamp", style="yellow")
    table.add_column("Content", style="white")
    table.add_column("Owner", style="green")

    for node_id, data in results:
        content = data.get('content', '')
        summary = content[:80] + '...' if len(content) > 80 else content
        timestamp = data.get('timestamp')
        ts_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "N/A"

        table.add_row(
            node_id[:8],
            data.get('type', 'N/A'),
            ts_str,
            summary.replace('\n', ' '),
            data.get('owner', 'N/A')
        )
    console.print(table)