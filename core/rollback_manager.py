from typing import Dict, List, Callable, Any
from core.system_state import SystemState

class RollbackManager:
    def __init__(self):
        self.history: List[SystemState] = []
        self.agent_snapshots: Dict[str, SystemState] = {}

    def save_snapshot(self, agent_name: str, state: SystemState):
        self.agent_snapshots[agent_name] = state.snapshot()

    def rollback(self, agent_name: str) -> SystemState:
        if agent_name in self.agent_snapshots:
            return self.agent_snapshots.pop(agent_name)
        else:
            raise Exception(f"No snapshot found for agent {agent_name}")

    def get_last_state(self) -> SystemState:
        if not self.history:
            raise Exception("No history available to rollback to.")
        return self.history[-1]

    def record_state(self, state: SystemState):
        self.history.append(state.snapshot())