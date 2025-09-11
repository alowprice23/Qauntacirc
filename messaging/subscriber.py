# messaging/subscriber.py

"""
High-level message subscriber with built-in features like automatic
deserialization, dead-letter queue handling, and circuit breakers.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from pybreaker import CircuitBreaker as circuit
from nats.aio.msg import Msg

from core.exceptions import QuantumStateError
from core.types import QCState
from messaging.nats_client import NATSClient, QuantumAwareCallback
from messaging.serialization import MessageSerializer, SerializationFormat

log = logging.getLogger(__name__)

# Type alias for the user-friendly callback, which receives deserialized data
DataCallback = Callable[[Any, Optional[QCState]], Awaitable[None]]

class MessageSubscriber:
    """
    Provides a high-level API for subscribing to NATS subjects and processing
    messages with added reliability features.
    """

    def __init__(
        self,
        nats_client: NATSClient,
        serializer: MessageSerializer,
        dlq_subject_prefix: str = "DLQ",
        max_delivery_attempts: int = 5,
    ):
        """
        Initializes the MessageSubscriber.

        Args:
            nats_client: An instance of the NATSClient.
            serializer: An instance of the MessageSerializer.
            dlq_subject_prefix: The prefix for Dead Letter Queue subjects.
            max_delivery_attempts: Max times a message should be delivered before DLQ.
        """
        if not isinstance(nats_client, NATSClient):
            raise TypeError("nats_client must be an instance of NATSClient.")
        if not isinstance(serializer, MessageSerializer):
            raise TypeError("serializer must be an instance of MessageSerializer.")

        self.nats_client = nats_client
        self.serializer = serializer
        self.dlq_subject_prefix = dlq_subject_prefix
        self.max_delivery_attempts = max_delivery_attempts
        self._subscriptions: Dict[str, bool] = {}

    def _validate_quantum_state(self, context: Optional[QCState]) -> None:
        """
        Validates the received quantum state context.
        """
        if context is None:
            return
        try:
            QCState.model_validate(context.model_dump())
            log.debug(f"Received quantum state context {context.id} passed validation.")
        except Exception as e:
            log.error(f"Invalid quantum state context received: {e}", exc_info=True)
            raise QuantumStateError("Invalid QCState received in message.") from e

    async def subscribe(
        self,
        subject: str,
        target_class: BaseModel | type,
        callback: DataCallback,
        queue: str = "",
        durable: Optional[str] = None,
        stream: Optional[str] = None,
        breaker_fail_max: int = 5,
        breaker_reset_timeout: int = 30,
    ):
        """
        Subscribes to a subject and processes messages using a circuit breaker.

        Args:
            subject: The subject to subscribe to.
            target_class: The Pydantic model or type to deserialize the payload into.
            callback: The async function to process the deserialized data.
            queue: The queue group name for load balancing.
            durable: The name for a durable consumer.
            stream: The name of the JetStream stream.
            breaker_fail_max: Max failures before opening the circuit breaker.
            breaker_reset_timeout: Seconds to wait before closing the breaker.
        """
        if subject in self._subscriptions:
            log.warning(f"Already subscribed to subject '{subject}'. Ignoring request.")
            return

        @circuit(fail_max=breaker_fail_max, reset_timeout=breaker_reset_timeout)
        async def process_message_with_breaker(msg: Msg, quantum_context: Optional[QCState]):
            """The core logic for processing a single message, wrapped in a circuit breaker."""
            try:
                # Check for poison pill message (exceeded delivery attempts)
                if msg.metadata.num_delivered > self.max_delivery_attempts:
                    log.warning(f"Message {msg.headers.get('Nats-Msg-Id')} exceeded max deliveries. Sending to DLQ.")
                    await self._send_to_dlq(msg, "MaxDeliveriesExceeded")
                    await msg.term() # Use term() for DLQ to prevent redelivery
                    return

                # 1. Validate quantum context
                self._validate_quantum_state(quantum_context)

                # 2. Deserialize payload
                headers = msg.headers or {}
                is_compressed = headers.get("X-Payload-Compressed") == "true"
                serialization_format_str = headers.get("X-Serialization-Format", "json")
                serialization_format = SerializationFormat(serialization_format_str)

                data = self.serializer.deserialize(
                    data=msg.data,
                    target_class=target_class,
                    format=serialization_format,
                    is_compressed=is_compressed,
                )

                # 3. Execute user callback
                await callback(data, quantum_context)

                # 4. Acknowledge message
                await msg.ack()
                log.debug(f"Successfully processed and ACK'd message on '{msg.subject}'.")

            except Exception as e:
                log.error(f"Failed to process message on '{msg.subject}': {e}", exc_info=True)
                # Signal NATS to redeliver the message after a delay
                await msg.nak(delay=5)
                # Re-raise to trip the circuit breaker
                raise

        async def wrapped_callback(msg: Msg, quantum_context: Optional[QCState]):
            try:
                await process_message_with_breaker(msg, quantum_context)
            except Exception as e:
                log.critical(f"Unhandled exception in subscriber for '{subject}': {e}", exc_info=True)
                # Should ideally not happen if _process_message is robust
                await msg.term()

        await self.nats_client.subscribe_quantum_aware(
            subject=subject,
            callback=wrapped_callback,
            queue=queue,
            durable=durable,
            stream=stream,
        )
        self._subscriptions[subject] = True
        log.info(f"Successfully subscribed to '{subject}' with circuit breaker.")

    async def _send_to_dlq(self, msg: Msg, reason: str):
        """Publishes a message to the Dead Letter Queue."""
        dlq_subject = f"{self.dlq_subject_prefix}.{msg.subject}"
        log.info(f"Sending message to DLQ: '{dlq_subject}'")

        dlq_headers = msg.headers or {}
        dlq_headers["X-DLQ-Reason"] = reason
        dlq_headers["X-Original-Subject"] = msg.subject

        try:
            # Use the core NATS client to publish to DLQ
            # We don't need the full publisher features here (like retries)
            await self.nats_client.js.publish(
                subject=dlq_subject,
                payload=msg.data,
                headers=dlq_headers
            )
        except Exception as e:
            log.critical(f"Could not publish message to DLQ subject '{dlq_subject}': {e}", exc_info=True)

    async def unsubscribe(self, subject: str):
        """
        Unsubscribes from a subject.

        Note: The underlying `nats-py` client manages the actual subscription object.
        This method is for cleaning up local state like circuit breakers.
        Actual unsubscription would need to be managed via the NATS client subscription object.
        """
        if subject in self._subscriptions:
            del self._subscriptions[subject]
            log.info(f"Removed circuit breaker for subject '{subject}'.")
        else:
            log.warning(f"No active subscription found for subject '{subject}' to unsubscribe.")
