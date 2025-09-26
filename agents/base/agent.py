from __future__ import annotations
from typing import Dict, Any
from uuid import UUID, uuid4
from core.system_state import SystemState

class QuantumAgent:
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.agent_id: UUID = uuid4()
        self.name = name
        self.config = config or {}

    def execute(self, state: SystemState, task: str) -> Dict[str, Any]:
        """
        Executes the agent's logic on the current state and returns a state delta.
        Subclasses must implement this method.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"QuantumAgent(name='{self.name}', id='{self.agent_id}')"