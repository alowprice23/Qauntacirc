from dataclasses import dataclass, field
from typing import Dict, Any
from uuid import UUID, uuid4

@dataclass
class VectorClock:
    """Represents a vector clock for tracking causality."""
    clocks: Dict[str, int] = field(default_factory=dict)

    def increment(self, agent_id: str):
        self.clocks[agent_id] = self.clocks.get(agent_id, 0) + 1

    def merge(self, other: 'VectorClock'):
        for agent_id, timestamp in other.clocks.items():
            self.clocks[agent_id] = max(self.clocks.get(agent_id, 0), timestamp)

@dataclass
class Message:
    """Represents a message passed between agents."""
    sender_id: str
    receiver_id: str
    topic: str
    payload: Any
    id: UUID = field(default_factory=uuid4)
    timestamp: VectorClock = field(default_factory=VectorClock)
    metadata: Dict[str, Any] = field(default_factory=dict)
