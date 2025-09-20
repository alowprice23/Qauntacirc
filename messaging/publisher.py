# messaging/publisher.py

"""
High-level message publisher with built-in features like retries,
batching, and idempotency.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any, List, Optional

from pydantic import BaseModel

from core.exceptions import MessagingError, QuantumStateError
from core.types import QCState
from messaging.nats_client import NATSMessageBus
from messaging.serialization import MessageSerializer, SerializationFormat

log = logging.getLogger(__name__)

class MessagePublisher:
    """
    Provides a high-level API for publishing messages to NATS, with added
    reliability and performance features.
    """

    def __init__(
        self,
        nats_client: NATSMessageBus,
        serializer: MessageSerializer,
        max_retries: int = 3,
        retry_delay_base: float = 0.5,
    ):
        """
        Initializes the MessagePublisher.

        Args:
            nats_client: An instance of the NATSMessageBus.
            serializer: An instance of the MessageSerializer.
            max_retries: The maximum number of times to retry publishing a message.
            retry_delay_base: The base delay in seconds for exponential backoff.
        """
        if not isinstance(nats_client, NATSMessageBus):
            raise TypeError("nats_client must be an instance of NATSMessageBus.")
        if not isinstance(serializer, MessageSerializer):
            raise TypeError("serializer must be an instance of MessageSerializer.")

        self.nats_client = nats_client
        self.serializer = serializer
        self.max_retries = max_retries
        self.retry_delay_base = retry_delay_base

    def _validate_quantum_state(self, context: QCState) -> None:
        """
        Validates the quantum state context before publishing.

        This is a hook for ensuring the QCState is consistent. For now, it
        checks the pydantic model's internal validation.

        Args:
            context: The QCState object to validate.
        """
        try:
            # Pydantic models are validated on instantiation, but we can re-validate.
            QCState.model_validate(context.model_dump())
            log.debug(f"Quantum state context {context.id} passed validation.")
        except Exception as e:
            log.error(f"Quantum state validation failed for context {context.id}: {e}", exc_info=True)
            raise QuantumStateError("Invalid QCState provided for publishing.") from e

    async def publish(
        self,
        subject: str,
        data: BaseModel | dict,
        quantum_context: Optional[QCState] = None,
        serialization_format: SerializationFormat = SerializationFormat.JSON,
        timeout: float = 2.0,
    ) -> str:
        """
        Serializes and publishes a single message with retry logic.

        Args:
            subject: The NATS subject to publish to.
            data: The data to publish (a Pydantic model or a dict).
            quantum_context: The optional quantum state context.
            serialization_format: The format for serializing the payload.
            timeout: The timeout for the entire publish operation, including retries.

        Returns:
            The unique message ID assigned to the message for idempotency.
        """
        start_time = time.monotonic()

        if quantum_context:
            self._validate_quantum_state(quantum_context)

        message_id = str(uuid.uuid4())

        payload, is_compressed = self.serializer.serialize(data, format=serialization_format)

        headers = {
            "Nats-Msg-Id": message_id,
            "X-Serialization-Format": serialization_format.value,
            "X-Payload-Compressed": "true" if is_compressed else "false",
        }

        for attempt in range(self.max_retries):
            try:
                await self.nats_client.publish_quantum_message(
                    subject=subject,
                    payload=payload,
                    quantum_context=quantum_context,
                    headers=headers,
                    timeout=timeout - (time.monotonic() - start_time) # Adjust timeout for retries
                )
                log.info(f"Successfully published message {message_id} to '{subject}' (attempt {attempt + 1})")
                return message_id
            except MessagingError as e:
                log.warning(f"Publish attempt {attempt + 1}/{self.max_retries} failed for subject '{subject}': {e}")
                if attempt + 1 >= self.max_retries:
                    log.error(f"Failed to publish message {message_id} to '{subject}' after {self.max_retries} attempts.")
                    raise

                delay = self.retry_delay_base * (2 ** attempt)
                await asyncio.sleep(delay)
            except Exception as e:
                log.error(f"An unexpected error occurred during publish: {e}", exc_info=True)
                raise

        # This part should be unreachable if max_retries > 0
        raise MessagingError(f"Failed to publish message {message_id} to '{subject}' after all retries.")

    async def publish_batch(
        self,
        subject: str,
        messages: List[tuple[BaseModel | dict, Optional[QCState]]],
        serialization_format: SerializationFormat = SerializationFormat.JSON,
        timeout: float = 10.0,
    ) -> List[str]:
        """
        Publishes a batch of messages concurrently.

        Note: This is a simple concurrent publisher, not a NATS core batch operation.

        Args:
            subject: The NATS subject to publish all messages to.
            messages: A list of tuples, where each tuple contains the data
                      and optional quantum_context for a message.
            serialization_format: The format for serializing all payloads.
            timeout: The timeout for publishing the entire batch.

        Returns:
            A list of the unique message IDs for each published message.
        """
        if not messages:
            return []

        publish_tasks = [
            self.publish(
                subject=subject,
                data=data,
                quantum_context=qc_context,
                serialization_format=serialization_format,
                timeout=timeout, # Each publish call gets the full timeout
            )
            for data, qc_context in messages
        ]

        results = await asyncio.gather(*publish_tasks, return_exceptions=True)

        # Process results, logging any errors
        successful_ids = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                log.error(f"Failed to publish message {i+1} in batch to '{subject}': {result}")
            else:
                successful_ids.append(result)

        if len(successful_ids) != len(messages):
            raise MessagingError(f"Only {len(successful_ids)}/{len(messages)} messages were published successfully to '{subject}'.")

        return successful_ids
