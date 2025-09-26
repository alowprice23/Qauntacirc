import json
from typing import Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel
from nats.aio.client import Client as NATS
from messaging.stream_manager import StreamManager
from core.system_state import SystemState

class StateChangeEvent(BaseModel):
    agent_name: str
    delta: Dict[str, Any]

class StateManager:
    def __init__(self, nats_client: NATS, stream_name: str = "system_state_events"):
        self.nats_client = nats_client
        self.stream_name = stream_name
        self.stream_manager = StreamManager(self.nats_client)

    async def initialize(self):
        await self.stream_manager.create_or_update_stream(
            self.stream_name, subjects=[f"{self.stream_name}.*"]
        )

    async def publish_state_change(self, agent_name: str, delta: Dict[str, Any]):
        event = StateChangeEvent(agent_name=agent_name, delta=delta)
        await self.nats_client.publish(
            f"{self.stream_name}.{agent_name}", event.model_dump_json().encode()
        )

    async def get_current_state(self, initial_state: SystemState) -> SystemState:
        current_state = initial_state.snapshot()

        async def message_handler(msg):
            nonlocal current_state
            event_data = json.loads(msg.data)
            event = StateChangeEvent(**event_data)
            current_state = current_state.apply_delta(event.delta)

        sub = await self.nats_client.subscribe(f"{self.stream_name}.*")
        try:
            while True:
                msg = await sub.next_msg(timeout=1.0)
                await message_handler(msg)
        except Exception:
            pass
        finally:
            await sub.unsubscribe()

        return current_state