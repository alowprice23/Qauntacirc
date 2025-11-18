from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from typing import Dict, List, Any, Optional
import math

class QuantumTable:
    """Base table formatter with quantum theming"""

    def __init__(self, title: str = "", console: Optional[Console] = None):
        self.console = console or Console()
        self.table = Table(title=title, show_header=True, header_style="bold blue")
        self._quantum_theme = {
            "energy": "bold green",
            "lyapunov": "bold yellow",
            "contraction": "bold cyan",
            "error": "bold red",
            "success": "bold green",
            "warning": "bold yellow"
        }

    def add_quantum_column(self, name: str, style: str = "white", **kwargs):
        """Add column with quantum theming"""
        self.table.add_column(name, style=style, **kwargs)
        return self

    def add_energy_row(self, label: str, value: float, unit: str = ""):
        """Add energy measurement row with formatting"""
        formatted_value = f"[energy]{value:.8f}[/energy] {unit}".strip()
        self.table.add_row(label, formatted_value)
        return self

    def add_measurement_row(self, label: str, value: float, measurement_type: str = "quantum"):
        """Add measurement row with appropriate styling"""
        style = self._quantum_theme.get(measurement_type, "white")
        formatted_value = f"[{style}]{value:.6f}[/{style}]"
        self.table.add_row(label, formatted_value)
        return self

    def render(self):
        """Render the table to console"""
        return self.table

class StatusTable(QuantumTable):
    """Specialized table for system status display"""

    def __init__(self, title: str = "System Status"):
        super().__init__(title)
        self.add_quantum_column("Metric", style="cyan")
        self.add_quantum_column("Value", style="white")
        self.add_quantum_column("Status", style="white")

    def add_status_row(self, metric: str, value: Any, status: str = "normal"):
        """Add status row with health indicators"""
        status_styles = {
            "healthy": "✅ [success]Healthy[/success]",
            "warning": "⚠️ [warning]Warning[/warning]",
            "critical": "❌ [error]Critical[/error]",
            "normal": "🔵 Normal"
        }

        status_display = status_styles.get(status, status)
        self.table.add_row(metric, str(value), status_display)
        return self

class MetricsTable(QuantumTable):
    """Table for displaying performance metrics"""

    def __init__(self, title: str = "Performance Metrics"):
        super().__init__(title)
        self.add_quantum_column("Metric", style="cyan")
        self.add_quantum_column("Current", style="white")
        self.add_quantum_column("Average", style="yellow")
        self.add_quantum_column("Trend", style="green")

    def add_metric_row(self, name: str, current: float, average: float, trend: str = "stable"):
        """Add metric row with trend indicators"""
        trend_indicators = {
            "up": "📈 [success]Rising[/success]",
            "down": "📉 [error]Falling[/error]",
            "stable": "➡️ [quantum]Stable[/quantum]"
        }

        trend_display = trend_indicators.get(trend, trend)
        self.table.add_row(name, f"{current:.4f}", f"{average:.4f}", trend_display)
        return self

def create_quantum_progress_table(operations: List[Dict[str, Any]]) -> Table:
    """Create table showing quantum operation progress"""
    table = Table(title="Quantum Operations")
    table.add_column("Operation", style="cyan")
    table.add_column("Phase", style="magenta")
    table.add_column("Progress", style="white")
    table.add_column("Energy Change", style="energy")

    for op in operations:
        progress_bar = f"[{'█' * int(op['progress'] * 10)}{'░' * (10 - int(op['progress'] * 10))}]"
        energy_change = op.get('energy_delta', 0)
        energy_display = f"[energy]{'▲' if energy_change > 0 else '▼'}{abs(energy_change):.6f}[/energy]"

        table.add_row(
            op['name'],
            op['phase'],
            f"{progress_bar} {op['progress']:.1%}",
            energy_display
        )

    return table

def create_mathematical_formula_panel(formula: str, description: str) -> Panel:
    """Create panel displaying mathematical formulas"""
    formula_text = Text(formula, style="bold cyan")
    description_text = Text(description, style="white")

    content = Text()
    content.append(formula_text)
    content.append("\n\n")
    content.append(description_text)

    return Panel(
        content,
        title="Mathematical Foundation",
        border_style="blue",
        padding=(1, 2)
    )

def format_energy_components(energy_data: Dict[str, float]) -> Table:
    """Format energy function components in a detailed table"""
    table = Table(title="Energy Function Decomposition: E_approx = E_static + E_dynamic + E_interaction")
    table.add_column("Component", style="cyan")
    table.add_column("Value", style="energy")
    table.add_column("Weight", style="yellow")
    table.add_column("Contribution", style="white")

    total_energy = sum(energy_data.values())

    for component, value in energy_data.items():
        weight = value / total_energy if total_energy > 0 else 0
        contribution = f"{weight:.1%}"

        table.add_row(
            component.replace("_", " ").title(),
            f"{value:.8f}",
            f"{weight:.3f}",
            contribution
        )

    # Add total row
    table.add_row(
        "[bold]Total (E_approx)[/bold]",
        f"[bold energy]{total_energy:.8f}[/bold energy]",
        "[bold]1.000[/bold]",
        "[bold]100%[/bold]"
    )

    return table
