import asyncio
from collections import defaultdict
from typing import Dict, List, Callable, Awaitable

from messaging.types import Message, VectorClock

class AgentRouter:
    """
    A simple in-memory message router for agent communication.
    This implementation simulates message passing with causal order tracking.
    """
    def __init__(self):
        self.mailboxes: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        self.subscriptions: Dict[str, List[str]] = defaultdict(list)
        self.vector_clocks: Dict[str, VectorClock] = defaultdict(VectorClock)

    def subscribe(self, agent_id: str, topic: str):
        """Subscribe an agent to a topic."""
        self.subscriptions[topic].append(agent_id)

    async def publish(self, message: Message):
        """Publish a message to a topic."""
        sender_id = message.sender_id

        # Increment sender's vector clock
        self.vector_clocks[sender_id].increment(sender_id)
        message.timestamp = self.vector_clocks[sender_id]

        for subscriber_id in self.subscriptions.get(message.topic, []):
            await self.mailboxes[subscriber_id].put(message)

    async def receive(self, agent_id: str) -> Message:
        """Receive a message from an agent's mailbox."""
        message = await self.mailboxes[agent_id].get()

        # Merge vector clocks to maintain causal history
        self.vector_clocks[agent_id].merge(message.timestamp)
        self.vector_clocks[agent_id].increment(agent_id)

        return message

    def get_vector_clock(self, agent_id: str) -> VectorClock:
        """Get the current vector clock for an agent."""
        return self.vector_clocks[agent_id]
