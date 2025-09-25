import asyncio
import logging
from typing import Dict, List, Optional

from core.types import (
    QuantaCircConfig, QCState, AgentTask, AgentResult, SoftwareState,
    EnergyComponents, Status
)
from messaging.nats_client import NATSClient
from messaging.publisher import MessagePublisher
from messaging.subscriber import MessageSubscriber
from messaging.serialization import MessageSerializer

log = logging.getLogger(__name__)

class Orchestrator:
    """
    Manages agent coordination, state evolution, and communication.
    """

    def __init__(self, config: QuantaCircConfig):
        self.config = config
        self.nats_client = NATSClient(
            server_urls=config.nats.server_url
        )
        serializer = MessageSerializer()
        self.publisher = MessagePublisher(self.nats_client, serializer)
        self.subscriber = MessageSubscriber(self.nats_client, serializer)

        self.agent_registry: Dict[str, Dict] = {}
        self.state_history: List[QCState] = []
        self._is_running = False
        self._pruner_task: Optional[asyncio.Task] = None

    async def _publish_status(self, message: str, status_type: str = "info", extra: Optional[Dict] = None):
        """Helper to publish status updates to the CLI."""
        payload = {"type": status_type, "message": message, "data": extra or {}}
        try:
            await self.publisher.publish(
                subject=self.config.orchestrator.status_topic,
                data=payload
            )
        except Exception as e:
            log.error(f"Failed to publish status update: {e}")

    def _select_agent_for_task(self, task_type: str) -> Optional[str]:
        """Selects a suitable agent from the registry based on capability."""
        for name, details in self.agent_registry.items():
            if task_type in details.get("capabilities", []):
                return name
        return None

    async def _prune_stale_agents(self, stale_threshold: int = 60):
        """Periodically removes agents that have not sent a heartbeat."""
        while self._is_running:
            await asyncio.sleep(stale_threshold / 2)
            try:
                now = asyncio.get_event_loop().time()
                stale_agents = [
                    name for name, details in self.agent_registry.items()
                    if now - details.get("last_seen", 0) > stale_threshold
                ]
                for name in stale_agents:
                    del self.agent_registry[name]
                    log.warning(f"Pruned stale agent: {name}")
                    await self._publish_status(f"Agent '{name}' has gone offline (timeout).", "agent_status")
            except Exception as e:
                log.error(f"Error during agent pruning: {e}")

    async def _handle_intent(self, payload: dict, context: Optional[QCState]):
        """Callback for handling incoming CLI intents."""
        intent_text = payload.get("text")
        if not intent_text:
            log.warning("Received intent with no text.")
            return

        log.info(f"Received intent: '{intent_text}'")
        await self._publish_status(f"Received intent: '{intent_text}'. Starting execution pipeline.")
        asyncio.create_task(self.execute_pipeline(intent_text))

    async def _handle_agent_announcement(self, payload: dict, context: Optional[QCState]):
        """Callback for agent registration and health checks."""
        agent_name = payload.get("name")
        if not agent_name:
            return

        self.agent_registry[agent_name] = {
            "name": agent_name,
            "capabilities": payload.get("capabilities", []),
            "last_seen": asyncio.get_event_loop().time()
        }
        log.info(f"Agent '{agent_name}' announced its presence with capabilities: {payload.get('capabilities')}")
        await self._publish_status(f"Agent '{agent_name}' is online.", "agent_status")

    async def start(self):
        """Connects to NATS and starts listening for messages."""
        if self._is_running:
            return

        await self.nats_client.connect()
        self._is_running = True
        self._pruner_task = asyncio.create_task(self._prune_stale_agents())
        log.info("Orchestrator started. Subscribing to topics.")

        await self.subscriber.subscribe(self.config.orchestrator.intent_topic, dict, self._handle_intent, "orchestrator_intent_queue")
        await self.subscriber.subscribe("qc.agent.announce", dict, self._handle_agent_announcement, "orchestrator_agent_listeners")

        await self._publish_status("Orchestrator is online and ready.", "system_status")

    async def stop(self):
        """Gracefully shuts down the orchestrator."""
        if not self._is_running:
            return
        self._is_running = False
        if self._pruner_task:
            self._pruner_task.cancel()
        await self.nats_client.disconnect()
        log.info("Orchestrator shut down.")

    async def execute_pipeline(self, requirement: str):
        """The main execution loop for processing a requirement."""
        task_type = "requirements_quantization"
        agent_name = self._select_agent_for_task(task_type)

        if not agent_name:
            await self._publish_status(f"No agent available for task '{task_type}'.", "error")
            return

        await self._publish_status(f"Engaging agent '{agent_name}' for '{task_type}'.")
        task = AgentTask(agent_name=agent_name, task_type=task_type, payload={"text": requirement})

        try:
            response_msg = await self.nats_client.request(
                subject=f"qc.agent.tasks.{agent_name}",
                payload=task.model_dump_json().encode(),
                timeout=15.0
            )
            result = AgentResult.model_validate_json(response_msg.data)

            if result.status == Status.FAILED:
                await self._publish_status(f"Agent '{agent_name}' declined task: {result.error}", "warning")
                return

            await self._publish_status(
                f"Agent '{agent_name}' completed task. Result: {result.result.get('message')}",
                "progress",
                extra={"agent": agent_name, "result": result.result}
            )
            # Here, you would continue the pipeline with subsequent tasks...
            await self._publish_status("Execution pipeline finished.", "complete")

        except asyncio.TimeoutError:
            await self._publish_status(f"Agent '{agent_name}' timed out. Removing from registry.", "error")
            if agent_name in self.agent_registry:
                del self.agent_registry[agent_name]
        except Exception as e:
            await self._publish_status(f"An error occurred while communicating with '{agent_name}': {e}", "error")
