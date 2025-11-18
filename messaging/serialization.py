# messaging/serialization.py

"""
Handles serialization, deserialization, and compression of messages.

This module provides a flexible serialization layer that supports multiple
formats (JSON, MessagePack, Protobuf) and transparently handles compression
for large messages. It is designed to be used by the MessagePublisher and
MessageSubscriber to prepare messages for transit and reconstruct them
upon receipt.
"""

from __future__ import annotations

import zlib
from enum import Enum
from typing import Any, Type, TypeVar

import msgpack
from pydantic import BaseModel

# Assuming protobuf is installed, but providing a fallback.
try:
    from google.protobuf.message import Message as ProtobufMessage
except ImportError:
    ProtobufMessage = None

from core.serialization import deserialize_model as deserialize_pydantic_model
from core.serialization import serialize_model as serialize_pydantic_model

# Generic type for Pydantic models
T = TypeVar("T", bound=BaseModel)

class SerializationFormat(str, Enum):
    """Supported serialization formats."""
    JSON = "json"
    MSGPACK = "msgpack"
    PROTOBUF = "protobuf"


class MessageSerializer:
    """
    Serializes and deserializes messages with support for multiple formats
    and optional compression.
    """

    def __init__(self, compress_threshold: int = 1024, compression_level: int = 6):
        """
        Initializes the MessageSerializer.

        Args:
            compress_threshold: The size in bytes above which messages should
                                be compressed. Set to 0 to always compress,
                                or a negative value to never compress.
            compression_level: The zlib compression level (1-9).
        """
        if not (-1 <= compression_level <= 9):
            raise ValueError("compression_level must be between -1 and 9.")
        self.compress_threshold = compress_threshold
        self.compression_level = compression_level

    def serialize(
        self,
        data: Any,
        format: SerializationFormat = SerializationFormat.JSON,
        schema_version: str = "v1",
    ) -> tuple[bytes, bool]:
        """
        Serializes data into bytes using the specified format.

        Args:
            data: The data to serialize (e.g., a Pydantic model).
            format: The serialization format to use.
            schema_version: The schema version, for formats that support it.

        Returns:
            A tuple containing the serialized data as bytes and a boolean
            indicating if the payload is compressed.
        """
        if format == SerializationFormat.JSON:
            if isinstance(data, BaseModel):
                # core.serialization returns a string, so we encode it
                raw_bytes = serialize_pydantic_model(data).encode("utf-8")
            else:
                # Fallback for non-pydantic types, though not the primary use case
                import json
                raw_bytes = json.dumps(data).encode("utf-8")
        elif format == SerializationFormat.MSGPACK:
            if isinstance(data, BaseModel):
                # Pydantic models need to be converted to dicts for msgpack
                raw_bytes = msgpack.packb(data.model_dump(mode='json'), use_bin_type=True)
            else:
                raw_bytes = msgpack.packb(data, use_bin_type=True)
        elif format == SerializationFormat.PROTOBUF:
            if ProtobufMessage and isinstance(data, ProtobufMessage):
                raw_bytes = data.SerializeToString()
            else:
                raise TypeError("Protobuf serialization requires a Protobuf Message object or protobuf library is not installed.")
        else:
            raise ValueError(f"Unsupported serialization format: {format}")

        # Check if compression is needed
        if self.compress_threshold >= 0 and len(raw_bytes) > self.compress_threshold:
            return zlib.compress(raw_bytes, self.compression_level), True
        return raw_bytes, False

    def deserialize(
        self,
        data: bytes,
        target_class: Type[T] | Type[ProtobufMessage],
        format: SerializationFormat = SerializationFormat.JSON,
        is_compressed: bool = False,
    ) -> T | ProtobufMessage:
        """
        Deserializes bytes into an object using the specified format.

        Args:
            data: The byte string to deserialize.
            target_class: The target class to instantiate (e.g., a Pydantic model).
            format: The serialization format used.
            is_compressed: A flag indicating if the data is compressed.

        Returns:
            An instance of the target class.
        """
        if is_compressed:
            payload = zlib.decompress(data)
        else:
            payload = data

        if format == SerializationFormat.JSON:
            if not isinstance(target_class, type) or not issubclass(target_class, BaseModel):
                 raise TypeError("JSON deserialization requires a Pydantic model class.")
            return deserialize_pydantic_model(payload.decode("utf-8"), target_class)
        elif format == SerializationFormat.MSGPACK:
            unpacked = msgpack.unpackb(payload, raw=False)
            if isinstance(target_class, type) and issubclass(target_class, BaseModel):
                return target_class.model_validate(unpacked)
            return unpacked
        elif format == SerializationFormat.PROTOBUF:
            if ProtobufMessage and isinstance(target_class, type) and issubclass(target_class, ProtobufMessage):
                instance = target_class()
                instance.ParseFromString(payload)
                return instance
            else:
                raise TypeError("Protobuf deserialization requires a Protobuf Message class or protobuf library is not installed.")
        else:
            raise ValueError(f"Unsupported serialization format: {format}")
