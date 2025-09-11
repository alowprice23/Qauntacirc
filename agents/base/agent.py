import abc
import uuid
from typing import Dict, Any, Optional, List

from core.state_space import StateSpace
from core.energy_calculator import EnergyCalculator
from core.types import AgentTask as Proposal, AgentResult as Action, QCState as State
from monitoring.metrics import QuantumMetrics as MetricsLogger
from .contracts import Contract
from .policies import PolicyEngine
from .memory import AgentMemory


class QuantumAgent(abc.ABC):
    """
    Abstract Base Class for all agents operating within the quantum computing framework.

    Each agent must implement methods for analyzing system state, validating proposals,
    and executing actions. The base class provides a structured lifecycle, contract
    enforcement, and integration with monitoring and memory systems.
    """
    def __init__(
        self,
        name: str,
        state_space: "StateSpace",
        energy_calculator: "EnergyCalculator",
        metrics_logger: "MetricsLogger",
        policy_engine: "PolicyEngine",
        agent_memory: "AgentMemory",
        contracts: Optional[List["Contract"]] = None,
        agent_id: Optional[str] = None,
    ):
        """
        Initializes the QuantumAgent.
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.state_space = state_space
        self.energy_calculator = energy_calculator
        self.metrics_logger = metrics_logger
        self.policy_engine = policy_engine
        self.agent_memory = agent_memory
        self.contracts = contracts or []
        self.is_active = False

        self.metrics_logger.register_counter(f"agent_{self.name}_proposals", "Number of proposals generated")
        self.metrics_logger.register_counter(f"agent_{self.name}_executions", "Number of successful executions")
        self.metrics_logger.register_histogram(f"agent_{self.name}_execution_duration", "Duration of agent execution")

    def initialize(self):
        """Initializes the agent's resources."""
        print(f"Agent {self.name} ({self.agent_id}) initialized.")

    def activate(self):
        """Activates the agent, making it ready to process tasks."""
        self.is_active = True
        print(f"Agent {self.name} ({self.agent_id}) activated.")

    def deactivate(self):
        """Deactivates the agent, releasing resources."""
        self.is_active = False
        print(f"Agent {self.name} ({self.agent_id}) deactivated.")

    @abc.abstractmethod
    def analyze_state(self, state: "State") -> "Proposal":
        """
        Analyzes the current system state and generates a proposal for action.
        """
        pass

    @abc.abstractmethod
    def validate_proposal(self, proposal: "Proposal") -> bool:
        """
        Validates a proposal against internal logic and constraints.
        """
        pass

    @abc.abstractmethod
    def execute(self, proposal: "Proposal") -> "Action":
        """
        Executes a validated proposal.
        """
        pass

    def _enforce_preconditions(self, state: "State"):
        """Enforces all preconditions defined in contracts."""
        for contract in self.contracts:
            if not contract.check_preconditions(state):
                raise ValueError(f"Precondition failed for contract {contract.name}")

    def _enforce_postconditions(self, state: "State", action: "Action"):
        """Enforces all postconditions defined in contracts."""
        for contract in self.contracts:
            if not contract.check_postconditions(state, action):
                raise ValueError(f"Postcondition failed for contract {contract.name}")

    def run(self, state: "State") -> Optional["Action"]:
        """
        The main execution loop for the agent.
        """
        if not self.is_active:
            print(f"Agent {self.name} is not active.")
            return None

        with self.metrics_logger.log_duration(f"agent_{self.name}_execution_duration"):
            try:
                self._enforce_preconditions(state)

                proposal = self.analyze_state(state)
                self.metrics_logger.increment_counter(f"agent_{self.name}_proposals")

                if not self.validate_proposal(proposal) or not self.policy_engine.validate(proposal):
                    return None

                action = self.execute(proposal)

                self._enforce_postconditions(state, action)

                self.metrics_logger.increment_counter(f"agent_{self.name}_executions")
                self.agent_memory.record_decision(state, proposal, action)

                return action

            except Exception as e:
                self.metrics_logger.increment_counter(f"agent_{self.name}_errors")
                print(f"Agent {self.name} failed execution: {e}")
                return None
