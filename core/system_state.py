from __future__ import annotations
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime
import copy

class SystemState(BaseModel):
    state_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def snapshot(self) -> SystemState:
        return self.model_copy(deep=True)

    def apply_delta(self, delta: Dict[str, Any]) -> SystemState:
        new_state = self.snapshot()
        new_state.data.update(delta)
        new_state.state_id = uuid4()
        new_state.timestamp = datetime.utcnow()
        return new_state