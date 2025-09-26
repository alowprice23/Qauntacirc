from typing import Dict, Any, Callable
from enum import Enum
from core.system_state import SystemState
from core.rollback_manager import RollbackManager

class RecoveryStrategy(Enum):
    CONTINUE = "continue"
    RETRY = "retry"
    HALT = "halt"

class FailureManager:
    def __init__(self, rollback_manager: RollbackManager):
        self.rollback_manager = rollback_manager
        self.agent_failure_counts: Dict[str, int] = {}

    def handle_failure(
        self,
        agent_name: str,
        exception: Exception,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.CONTINUE,
        max_retries: int = 3
    ) -> SystemState:
        print(f"Handling failure for agent {agent_name}: {exception}")
        self.agent_failure_counts[agent_name] = self.agent_failure_counts.get(agent_name, 0) + 1

        if recovery_strategy == RecoveryStrategy.RETRY and self.agent_failure_counts[agent_name] < max_retries:
            print(f"Retrying agent {agent_name}...")
            # In a real implementation, you would re-execute the agent.
            # Here, we'll just return the rolled-back state.
            return self.rollback_manager.rollback(agent_name)

        if recovery_strategy == RecoveryStrategy.HALT:
            print(f"Halting execution due to failure in agent {agent_name}.")
            raise exception

        # Default to CONTINUE
        print(f"Continuing execution after failure in agent {agent_name}.")
        return self.rollback_manager.rollback(agent_name)