import asyncio
import logging
from typing import Any, Optional

from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

from core.types import QuantaCircConfig, QCState, AgentTask
from messaging.nats_client import NATSClient
from messaging.publisher import MessagePublisher
from messaging.subscriber import MessageSubscriber
from messaging.serialization import MessageSerializer, SerializationFormat

log = logging.getLogger(__name__)

class CLIBridge:
    """
    Manages the communication bridge between the CLI and the orchestrator.
    """

    def __init__(self, config: QuantaCircConfig, console: Console):
        self.config = config
        self.console = console
        self.nats_client: Optional[NATSClient] = None
        self.publisher: Optional[MessagePublisher] = None
        self.subscriber: Optional[MessageSubscriber] = None
        self.is_connected = False

    async def connect(self):
        """
        Initializes the NATS client and messaging components.
        """
        if self.is_connected:
            return

        self.console.print("[bold blue]Connecting to QuantaCirc messaging system...[/bold blue]")
        try:
            self.nats_client = NATSClient(
                server_urls=self.config.nats.server_url
            )
            await self.nats_client.connect()

            serializer = MessageSerializer()
            self.publisher = MessagePublisher(self.nats_client, serializer)
            self.subscriber = MessageSubscriber(self.nats_client, serializer)

            # Subscribe to orchestrator status updates
            await self.subscriber.subscribe(
                subject=self.config.orchestrator.status_topic,
                target_class=dict, # For now, just receive dicts
                callback=self._handle_status_update,
                queue="cli_status_listeners"
            )

            self.is_connected = True
            self.console.print("[bold green]Successfully connected to messaging system.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]Failed to connect to messaging system: {e}[/bold red]")
            self.is_connected = False
            raise

    async def disconnect(self):
        """
        Disconnects from the NATS server.
        """
        if self.nats_client and self.is_connected:
            await self.nats_client.disconnect()
            self.is_connected = False
            self.console.print("[bold blue]Disconnected from messaging system.[/bold blue]")

    async def send_intent(self, intent_text: str, conversation_id: Optional[str] = None):
        """
        Publishes a user's intent to the orchestrator.
        """
        if not self.publisher:
            raise ConnectionError("Bridge is not connected. Cannot send intent.")

        intent_payload = {
            "text": intent_text,
            "conversation_id": conversation_id,
        }

        self.console.print(f"Sending intent: '[italic]{intent_text}[/italic]'")

        await self.publisher.publish(
            subject=self.config.orchestrator.intent_topic,
            data=intent_payload,
        )
        self.console.print("[green]Intent sent to orchestrator.[/green]")

    async def _handle_status_update(self, data: dict, quantum_context: Optional[QCState]):
        """
        Callback for processing status updates from the orchestrator.
        """
        # For now, just print the raw status update
        self.console.print(f"[bold yellow]Orchestrator Status:[/bold yellow] {data}")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()