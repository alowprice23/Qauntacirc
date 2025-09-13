# agents/base/metrics.py
"""
Provides a dedicated metrics collection class for agents, building on top
of the core monitoring framework.
"""

from monitoring.metrics import QuantumMetrics as MetricsLogger
from core.data_models import QCState as State, AgentResult as Action
from core.energy_calculator import EnergyCalculator


class AgentMetrics:
    """
    A specialized metrics collector for a single agent.

    This class provides a convenient interface for tracking common agent-related
    metrics and calculating derived ones like success rates.
    """
    def __init__(self, agent_name: str, metrics_logger: MetricsLogger, energy_calculator: EnergyCalculator):
        self.agent_name = agent_name
        self.logger = metrics_logger
        self.energy_calculator = energy_calculator

        self.prefix = f"agent_{self.agent_name}"

        # Core counters
        self.logger.register_counter(f"{self.prefix}_proposals", "Number of proposals generated")
        self.logger.register_counter(f"{self.prefix}_executions", "Number of successful executions")
        self.logger.register_counter(f"{self.prefix}_errors", "Number of errors encountered")

        # Histograms
        self.logger.register_histogram(f"{self.prefix}_execution_duration_seconds", "Execution duration in seconds")
        self.logger.register_histogram(f"{self.prefix}_energy_impact", "Energy impact of executed actions")

    def track_proposal(self):
        """Increments the proposals counter."""
        self.logger.increment_counter(f"{self.prefix}_proposals")

    def track_execution(self, duration_seconds: float, action: Action, initial_state: State):
        """
        Tracks a successful execution, including its duration and energy impact.
        """
        self.logger.increment_counter(f"{self.prefix}_executions")
        self.logger.observe_histogram(f"{self.prefix}_execution_duration_seconds", duration_seconds)

        # Calculate and track energy impact
        energy_impact = self.energy_calculator.calculate_action_energy(action)
        if energy_impact is not None:
            self.logger.observe_histogram(f"{self.prefix}_energy_impact", energy_impact)

    def track_error(self):
        """Increments the errors counter."""
        self.logger.increment_counter(f"{self.prefix}_errors")

    def get_success_rate(self) -> float:
        """
        Calculates the success rate of the agent.
        Note: This requires the underlying logger to expose its current values,
              which we assume it does for this example.
        """
        proposals = self.logger.get_counter_value(f"{self.prefix}_proposals")
        executions = self.logger.get_counter_value(f"{self.prefix}_executions")

        if proposals == 0:
            return 1.0  # Or 0.0, depending on definition. No proposals means no failures.

        return executions / proposals
