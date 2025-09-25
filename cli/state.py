import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ConversationState:
    """
    Manages the state of a single conversation with the QuantaCirc system.
    """
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    history: List[Dict[str, str]] = field(default_factory=list)
    project_state: Dict[str, Any] = field(default_factory=dict)
    active_agents: List[str] = field(default_factory=list)
    energy_metrics: Dict[str, float] = field(default_factory=dict)
    current_intent: Optional[str] = None

    def add_user_message(self, message: str):
        """Adds a user message to the history."""
        self.history.append({"role": "user", "content": message})
        self.current_intent = message

    def add_assistant_message(self, message: str):
        """Adds an assistant message to the history."""
        self.history.append({"role": "assistant", "content": message})

    def update_from_status(self, status_data: Dict[str, Any]):
        """Updates state from an orchestrator status message."""
        message = status_data.get("message", "")
        self.add_assistant_message(message)

        data = status_data.get("data", {})
        if "agent" in data:
            if data["agent"] not in self.active_agents:
                self.active_agents.append(data["agent"])

        if "energy_reduction" in data:
            current_total_reduction = self.energy_metrics.get("total_reduction", 0.0)
            self.energy_metrics["total_reduction"] = current_total_reduction + data["energy_reduction"]

    def get_context(self) -> Dict[str, Any]:
        """Returns a summary of the current state for context."""
        return {
            "conversation_id": self.conversation_id,
            "history_length": len(self.history),
            "last_intent": self.current_intent,
            "active_agents": self.active_agents,
        }