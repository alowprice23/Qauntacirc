import abc
import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, List, Tuple

from nats.aio.msg import Msg

from core.types import (
    QuantaCircConfig, AgentTask, AgentResult, QCState, Status
)
from messaging.nats_client import NATSClient
from messaging.publisher import MessagePublisher
from messaging.subscriber import MessageSubscriber
from messaging.serialization import MessageSerializer

log = logging.getLogger(__name__)

class QuantumAgent(abc.ABC):
    """
    Abstract Base Class for message-aware agents with full life-cycle and
    request-reply handling.
    """
    def __init__(self, name: str, config: QuantaCircConfig, agent_id: Optional[str] = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.config = config

        self.nats_client = NATSClient(
            server_urls=config.nats.server_url
        )
        self.serializer = MessageSerializer()
        self._is_running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._task_subscription = None

    @property
    @abc.abstractmethod
    def capabilities(self) -> List[str]:
        """A list of capabilities this agent provides."""
        pass

    async def connect(self):
        if not self.nats_client.is_connected:
            await self.nats_client.connect()
            log.info(f"Agent {self.name} connected to NATS.")

    async def disconnect(self):
        if self.nats_client.is_connected:
            await self.nats_client.disconnect()
            log.info(f"Agent {self.name} disconnected from NATS.")

    async def announce(self):
        """Announces the agent's presence."""
        announcement_payload = {"name": self.name, "agent_id": self.agent_id, "capabilities": self.capabilities}
        await self.nats_client.publish(subject="qc.agent.announce", payload=self.serializer.serialize(announcement_payload)[0])

    async def _heartbeat(self, interval: int = 30):
        while self._is_running:
            try:
                await self.announce()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Agent {self.name} heartbeat failed: {e}")
                await asyncio.sleep(interval)

    async def _handle_task(self, msg: Msg):
        """Handles incoming tasks from the orchestrator."""
        try:
            task = AgentTask.model_validate_json(msg.data)

            can_handle, reason = self.can_handle(task)
            if not can_handle:
                result = AgentResult(
                    task_id=task.id,
                    agent_name=self.name,
                    action_taken=False,
                    status=Status.FAILED,
                    error=f"Precondition not met: {reason}"
                )
            else:
                result = await self.process_task(task)

            await self.nats_client.publish(subject=msg.reply, payload=result.model_dump_json().encode())

        except Exception as e:
            log.error(f"Error processing task: {e}", exc_info=True)
            # Optionally, publish an error result back
            if 'task' in locals() and msg.reply:
                error_result = AgentResult(task_id=task.id, agent_name=self.name, status=Status.FAILED, error=str(e))
                await self.nats_client.publish(subject=msg.reply, payload=error_result.model_dump_json().encode())

    async def start(self):
        """Starts the agent's services, including heartbeat and task subscription."""
        if self._is_running: return
        self._is_running = True
        await self.connect()

        # Subscribe to dedicated task topic
        task_subject = f"qc.agent.tasks.{self.name}"
        self._task_subscription = await self.nats_client.subscribe(task_subject, callback=self._handle_task, queue=f"{self.name}_queue")

        self._heartbeat_task = asyncio.create_task(self._heartbeat())
        log.info(f"Agent {self.name} started and listening on '{task_subject}'.")

    async def stop(self):
        """Stops the agent's services."""
        if not self._is_running: return
        self._is_running = False

        if self._task_subscription:
            await self._task_subscription.unsubscribe()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try: await self._heartbeat_task
            except asyncio.CancelledError: pass

        await self.disconnect()
        log.info(f"Agent {self.name} stopped.")

    def can_handle(self, task: AgentTask) -> Tuple[bool, str]:
        """
        Checks if the agent can handle the given task.
        Override this method to implement precondition checks.
        """
        return True, ""

    @abc.abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Processes a task assigned by the orchestrator."""
        pass
