# messaging/__init__.py

"""
QuantaCirc Messaging System.

This package provides the core infrastructure for asynchronous, quantum-aware
communication between system components using NATS JetStream.
"""

from .nats_client import NATSClient
from .publisher import MessagePublisher
from .subscriber import MessageSubscriber
from .stream_manager import StreamManager
from .topic_manager import TopicManager
from .serialization import MessageSerializer, SerializationFormat

__all__ = [
    "NATSClient",
    "MessagePublisher",
    "MessageSubscriber",
    "StreamManager",
    "TopicManager",
    "MessageSerializer",
    "SerializationFormat",
]
