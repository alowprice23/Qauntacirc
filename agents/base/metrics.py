from core.metrics import get_system_metrics
import time
from contextlib import contextmanager
from dataclasses import field

# from core.types import AgentResult # To be uncommented later

# Placeholder for core.types
class AgentResult:
    action_taken: bool = False
    error: bool = False
    energy_delta: dict = field(default_factory=dict)
    proposal_generated: bool = False
    resource_usage: dict = field(default_factory=dict)


class AgentMetrics:
    """
    A helper class for agents to record their metrics.

    This class provides a simple interface for agents to interact with the
    centralized monitoring system, abstracting away the details of metrics
    collection.
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.metrics = get_system_metrics()

    def record_execution(self, result: AgentResult, duration: float):
        """
        Records the metrics for a single agent execution.

        Args:
            result: The result of the agent's execution.
            duration: The time taken for the execution in seconds.
        """
        self.metrics.record_agent_execution(self.agent_name, result, duration)

    @contextmanager
    def execution_timer(self, result: AgentResult):
        """
        A context manager to time an agent's execution and record metrics.

        This is a convenient way to ensure that execution time is always
        recorded, even if errors occur.

        Usage:
            agent_metrics = AgentMetrics("MyAgent")
            result = AgentResult()
            with agent_metrics.execution_timer(result):
                # Agent's logic here...
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_execution(result, duration)

    def proposal_generated(self, accepted: bool):
        """
        Records that a proposal was generated.
        """
        self.metrics.agent_proposals_counter.labels(
            agent_name=self.agent_name,
            accepted='true' if accepted else 'false'
        ).inc()