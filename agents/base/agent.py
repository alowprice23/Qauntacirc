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
from llm.factory import get_llm_client
from llm.client import LLMClient

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

        # Initialize LLM clients with fallback support
        self.llm_clients: List[LLMClient] = []
        providers = [config.llm.provider] + config.llm.fallback_providers
        unique_providers = list(dict.fromkeys(providers)) # Remove duplicates, preserve order

        for provider in unique_providers:
            try:
                client = get_llm_client(
                    provider=provider,
                    api_key=config.llm.api_key, # Factory will use env var if this is None
                    model=config.llm.model,
                )
                self.llm_clients.append(client)
            except Exception as e:
                log.error(f"Failed to initialize LLM client for provider {provider}: {e}")

        if not self.llm_clients:
            log.critical("No LLM clients could be initialized. Agent may not function correctly.")
            self.llm_client = None # No primary client
        else:
            self.llm_client = self.llm_clients[0]

        self._is_running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._task_subscription = None

    async def llm_generate_with_fallback(self, prompt: str, **kwargs: Any) -> str:
        """
        Generates text using the primary LLM client, with fallback to others on failure.
        """
        if not self.llm_clients:
            raise RuntimeError("No LLM clients are configured.")

        last_exception = None
        for client in self.llm_clients:
            try:
                log.info(f"Attempting LLM generation with {client.model} via {type(client).__name__}")
                return await client.generate(prompt, **kwargs)
            except Exception as e:
                last_exception = e
                log.warning(f"LLM client {type(client).__name__} failed: {e}. Trying next fallback.")

        raise RuntimeError(f"All LLM clients failed. Last error: {last_exception}") from last_exception

    async def llm_chat_with_fallback(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Generates a chat response using the primary LLM client, with fallback.
        """
        if not self.llm_clients:
            raise RuntimeError("No LLM clients are configured.")

        last_exception = None
        for client in self.llm_clients:
            try:
                log.info(f"Attempting LLM chat with {client.model} via {type(client).__name__}")
                return await client.chat(messages, **kwargs)
            except Exception as e:
                last_exception = e
                log.warning(f"LLM client {type(client).__name__} failed: {e}. Trying next fallback.")

        raise RuntimeError(f"All LLM clients failed. Last error: {last_exception}") from last_exception

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
