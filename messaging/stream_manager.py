# messaging/stream_manager.py

"""
Manages the lifecycle of NATS JetStream streams and consumers.
"""

from __future__ import annotations

import logging
from typing import Optional

from nats.js.api import ConsumerConfig, StreamConfig, StreamInfo, StreamState
from nats.js.errors import APIError

from core.exceptions import MessagingError
from messaging.nats_client import NATSMessageBus

log = logging.getLogger(__name__)

class StreamManager:
    """
    Provides an administrative interface for creating, updating, and deleting
    JetStream streams and consumers.
    """

    def __init__(self, nats_client: NATSMessageBus):
        """
        Initializes the StreamManager.

        Args:
            nats_client: An instance of the NATSMessageBus, which must be connected.
        """
        if not isinstance(nats_client, NATSMessageBus):
            raise TypeError("nats_client must be an instance of NATSMessageBus.")
        self.nats_client = nats_client

    async def _get_jsm(self):
        """Helper to get the JetStream context, ensuring the client is connected."""
        await self.nats_client._ensure_connected()
        return self.nats_client.js

    async def create_or_update_stream(
        self,
        stream_name: str,
        config: Optional[StreamConfig] = None,
        subjects: Optional[list[str]] = None,
    ) -> StreamInfo:
        """
        Creates a new stream or updates an existing one with the given configuration.

        Args:
            stream_name: The name of the stream.
            config: A complete StreamConfig object. If None, a basic config
                    will be generated from the subjects.
            subjects: A list of subjects for the stream. Used if config is None.

        Returns:
            The StreamInfo of the created or updated stream.
        """
        js = await self._get_jsm()

        if config is None:
            if subjects is None:
                raise ValueError("Either 'config' or 'subjects' must be provided.")
            config = StreamConfig(name=stream_name, subjects=subjects)

        # Ensure the name in the config matches the provided stream_name
        config.name = stream_name

        try:
            stream_info = await js.update_stream(config)
            log.info(f"Successfully updated stream '{stream_name}'.")
        except APIError as e:
            if e.err_code == 10059:  # Stream not found
                log.info(f"Stream '{stream_name}' not found, creating it now.")
                stream_info = await js.add_stream(config)
                log.info(f"Successfully created stream '{stream_name}'.")
            else:
                raise MessagingError(f"Stream operation failed for '{stream_name}'") from e
        except Exception as e:
            log.error(f"Failed to create or update stream '{stream_name}': {e}", exc_info=True)
            raise MessagingError(f"Stream operation failed for '{stream_name}'") from e

        return stream_info

    async def delete_stream(self, stream_name: str) -> bool:
        """
        Deletes a stream from the server.

        Args:
            stream_name: The name of the stream to delete.

        Returns:
            True if the stream was successfully deleted.
        """
        js = await self._get_jsm()
        try:
            success = await js.delete_stream(name=stream_name)
            if success:
                log.info(f"Successfully deleted stream '{stream_name}'.")
            else:
                log.warning(f"Failed to delete stream '{stream_name}' but no error was raised.")
            return success
        except APIError as e:
            if e.err_code == 10059:  # Stream not found
                log.warning(f"Attempted to delete non-existent stream '{stream_name}'.")
                return True  # Idempotent, it's already gone.
            else:
                log.error(f"API error while deleting stream '{stream_name}': {e}", exc_info=True)
                raise MessagingError(f"Failed to delete stream '{stream_name}'") from e
        except Exception as e:
            log.error(f"Failed to delete stream '{stream_name}': {e}", exc_info=True)
            raise MessagingError(f"Failed to delete stream '{stream_name}'") from e

    async def get_stream_info(self, stream_name: str) -> Optional[StreamInfo]:
        """
        Retrieves information about a specific stream.

        Args:
            stream_name: The name of the stream.

        Returns:
            A StreamInfo object, or None if the stream does not exist.
        """
        js = await self._get_jsm()
        try:
            return await js.stream_info(stream_name)
        except StreamNotFoundError:
            return None
        except Exception as e:
            log.error(f"Failed to get info for stream '{stream_name}': {e}", exc_info=True)
            raise MessagingError(f"Failed to get info for stream '{stream_name}'") from e

    async def get_stream_state(self, stream_name: str) -> Optional[StreamState]:
        """
        Retrieves the state (metrics) of a specific stream.

        Args:
            stream_name: The name of the stream.

        Returns:
            A StreamState object, or None if the stream does not exist.
        """
        info = await self.get_stream_info(stream_name)
        return info.state if info else None

    async def create_or_update_consumer(self, stream_name: str, config: ConsumerConfig) -> None:
        """
        Creates or updates a consumer for a given stream.

        Args:
            stream_name: The name of the stream the consumer belongs to.
            config: The ConsumerConfig object.
        """
        js = await self._get_jsm()
        try:
            await js.add_consumer(stream_name=stream_name, config=config)
            log.info(f"Successfully created/updated consumer '{config.durable_name}' on stream '{stream_name}'.")
        except Exception as e:
            log.error(f"Failed to create/update consumer on stream '{stream_name}': {e}", exc_info=True)
            raise MessagingError("Failed to create/update consumer") from e

    async def delete_consumer(self, stream_name: str, consumer_name: str) -> bool:
        """
        Deletes a durable consumer from a stream.

        Args:
            stream_name: The name of the stream.
            consumer_name: The durable name of the consumer to delete.

        Returns:
            True if the consumer was successfully deleted.
        """
        js = await self._get_jsm()
        try:
            success = await js.delete_consumer(stream_name=stream_name, consumer=consumer_name)
            if success:
                log.info(f"Successfully deleted consumer '{consumer_name}' from stream '{stream_name}'.")
            return success
        except Exception as e:
            log.error(f"Failed to delete consumer '{consumer_name}' from stream '{stream_name}': {e}", exc_info=True)
            raise MessagingError("Failed to delete consumer") from e
