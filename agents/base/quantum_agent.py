from abc import ABC, abstractmethod
from agents.base.agent import PhysicsBasedAgent
from core.types import SystemState
from agents.base.contracts import Proposal

class QuantumAgent(PhysicsBasedAgent, ABC):
    """
    A quantum agent that can guard and propose changes to the system state.
    """

    @abstractmethod
    def guard(self, state: SystemState) -> bool:
        """
        Checks if the agent should be activated based on the current system state.
        """
        pass

    @abstractmethod
    def propose(self, state: SystemState) -> Proposal:
        """
        Proposes a change to the system state.
        """
        pass
