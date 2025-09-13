# messaging/nats_client.py

"""
Core NATS client for managing connections, JetStream contexts, and providing
quantum-aware messaging primitives.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Awaitable, Callable, Dict, List, Optional

import nats
from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.js.api import StreamConfig
from nats.js.client import JetStreamContext

from core.exceptions import MessagingError
from core.serialization import deserialize_model, serialize_model
from core.data_models import QCState

log = logging.getLogger(__name__)

# Type alias for a quantum-aware message handler
QuantumAwareCallback = Callable[[Msg, Optional[QCState]], Awaitable[None]]

class NATSClient:
    """
    A high-level asynchronous client for NATS and JetStream with built-in
    support for quantum state context propagation.
    """

    def __init__(
        self,
        server_urls: List[str] | str,
        client_name: str = "QuantaCirc_NATSClient",
        connect_timeout: int = 10,
        reconnect_time_wait: int = 5,
    ):
        """
        Initializes the NATSClient.

        Args:
            server_urls: A list of NATS server URLs to connect to.
            client_name: A descriptive name for this client connection.
            connect_timeout: Timeout in seconds for the initial connection.
            reconnect_time_wait: Time in seconds to wait between reconnect attempts.
        """
        self.server_urls = server_urls
        self.client_name = client_name
        self.connect_timeout = connect_timeout
        self.reconnect_time_wait = reconnect_time_wait

        self.nc: Optional[NATS] = None
        self.js: Optional[JetStreamContext] = None
        self._connection_lock = asyncio.Lock()
        self._is_connected = False

    async def connect(self) -> None:
        """
        Establishes a connection to the NATS server(s) and enables JetStream.

        This method includes retry logic and ensures that if a connection is
        lost, the client will attempt to reconnect automatically.
        """
        async with self._connection_lock:
            if self._is_connected and self.nc and self.nc.is_connected:
                log.info("Already connected to NATS.")
                return

            log.info(f"Connecting to NATS servers: {self.server_urls}...")
            try:
                self.nc = await nats.connect(
                    servers=self.server_urls,
                    name=self.client_name,
                    connect_timeout=self.connect_timeout,
                    reconnect_time_wait=self.reconnect_time_wait,
                    error_cb=self._error_callback,
                    reconnected_cb=self._reconnected_callback,
                    disconnected_cb=self._disconnected_callback,
                    closed_cb=self._closed_callback,
                )
                self.js = self.nc.jetstream()
                self._is_connected = True
                log.info(f"Successfully connected to NATS server: {self.nc.connected_url.netloc}")
            except Exception as e:
                log.error(f"Failed to connect to NATS: {e}", exc_info=True)
                self._is_connected = False
                raise MessagingError("Could not establish NATS connection") from e

    async def disconnect(self) -> None:
        """
        Gracefully closes the connection to the NATS server.
        """
        async with self._connection_lock:
            if self.nc and not self.nc.is_closed:
                log.info("Disconnecting from NATS...")
                await self.nc.close()
            self._is_connected = False
            log.info("NATS connection closed.")

    async def _ensure_connected(self) -> None:
        """
        Verifies that the client is connected, raising an error if not.
        """
        if not self._is_connected or not self.nc or not self.nc.is_connected or not self.js:
            log.warning("NATS client is not connected. Attempting to reconnect...")
            await self.connect()
            if not self._is_connected:
                 raise MessagingError("NATS client is not connected.")

    @staticmethod
    def _encode_quantum_context(context: QCState) -> Dict[str, str]:
        """
        Serializes a QCState object into a format suitable for message headers.
        """
        if not isinstance(context, QCState):
            raise TypeError("context must be a QCState object.")
        # We serialize the full QCState model to a JSON string.
        # This is simpler than breaking it into individual header fields and
        # more robust to future changes in the QCState model.
        return {"X-Quantum-Context": serialize_model(context)}

    @staticmethod
    def _decode_quantum_context(headers: Optional[Dict[str, str]]) -> Optional[QCState]:
        """
        Deserializes a QCState object from message headers.
        """
        if not headers:
            return None

        context_str = headers.get("X-Quantum-Context")
        if not context_str:
            return None

        try:
            return deserialize_model(context_str, QCState)
        except (json.JSONDecodeError, TypeError) as e:
            log.error(f"Failed to decode quantum context from headers: {e}", exc_info=True)
            return None

    async def publish_quantum_message(
        self,
        subject: str,
        payload: bytes,
        quantum_context: Optional[QCState] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 1.0,
    ) -> None:
        """
        Publishes a message with an optional quantum state context and other headers.

        The quantum context is serialized and added to the message headers.

        Args:
            subject: The subject to publish the message to.
            payload: The message payload as bytes.
            quantum_context: The optional QCState to attach to the message.
            headers: An optional dictionary of additional headers.
            timeout: The timeout for the publish acknowledgment.
        """
        await self._ensure_connected()

        final_headers = headers.copy() if headers else {}
        if quantum_context:
            final_headers.update(self._encode_quantum_context(quantum_context))

        log.debug(f"Publishing message to '{subject}' with context: {bool(quantum_context)} and {len(final_headers)} headers")
        try:
            # js.publish expects headers to be None if empty, not {}
            await self.js.publish(subject, payload, timeout=timeout, headers=final_headers or None)
        except Exception as e:
            log.error(f"Failed to publish message to '{subject}': {e}", exc_info=True)
            raise MessagingError(f"Publish failed for subject '{subject}'") from e

    async def subscribe_quantum_aware(
        self,
        subject: str,
        callback: QuantumAwareCallback,
        queue: str = "",
        durable: Optional[str] = None,
        stream: Optional[str] = None,
    ) -> None:
        """
        Subscribes to a subject and processes messages with a quantum-aware callback.

        The callback receives both the message and the decoded QCState context.

        Args:
            subject: The subject to subscribe to.
            callback: An async function to call with the message and QCState.
            queue: The queue group name, for load-balancing.
            durable: The name of the durable consumer.
            stream: The name of the stream to subscribe to.
        """
        await self._ensure_connected()

        async def wrapped_callback(msg: Msg):
            """Internal callback to decode context before calling user function."""
            quantum_context = self._decode_quantum_context(msg.headers)
            log.debug(f"Received message on '{msg.subject}' with context: {bool(quantum_context)}")
            try:
                await callback(msg, quantum_context)
            except Exception as e:
                log.error(f"Error in quantum-aware callback for subject '{msg.subject}': {e}", exc_info=True)
                # Here you might add logic to NAK the message, etc.

        log.info(f"Subscribing to '{subject}' (Queue: '{queue or 'N/A'}', Durable: '{durable or 'N/A'}')")
        try:
            if stream:
                # This is a JetStream push consumer
                await self.js.subscribe(
                    subject=subject,
                    queue=queue,
                    durable=durable,
                    cb=wrapped_callback,
                )
            else:
                # This is a core NATS subscription
                await self.nc.subscribe(subject, queue=queue, cb=wrapped_callback)
        except Exception as e:
            log.error(f"Failed to subscribe to subject '{subject}': {e}", exc_info=True)
            raise MessagingError(f"Subscription failed for subject '{subject}'") from e

    # --- Connection Callbacks ---
    async def _error_callback(self, e: Exception):
        log.error(f"NATS connection error: {e}", exc_info=True)

    async def _reconnected_callback(self):
        log.warning(f"Reconnected to NATS server: {self.nc.connected_url.netloc}")
        self._is_connected = True

    async def _disconnected_callback(self):
        log.warning("Disconnected from NATS server. Attempting to reconnect...")
        self._is_connected = False

    async def _closed_callback(self):
        log.warning("NATS connection is permanently closed.")
        self._is_connected = False
