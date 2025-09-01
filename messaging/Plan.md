# Plan for the `messaging` Directory - Complete Implementation Guide

## 1. Architecture Overview & Philosophy

The `messaging` directory implements a robust, scalable messaging infrastructure using NATS JetStream for asynchronous communication between QuantaCirc components. This package provides the communication backbone enabling the ten specialized agents to coordinate, share state updates, and maintain system coherence while preserving quantum-mechanical principles.

### Core Design Principles

1. **Asynchronous Decoupling**: All agents communicate through message passing, ensuring loose coupling and scalability
2. **Event Sourcing**: All system changes are captured as immutable events with complete audit trails
3. **Quantum State Consistency**: Message ordering preserves quantum state evolution causality
4. **Fault Tolerance**: Built-in resilience with message persistence, redelivery, and dead letter handling
5. **Schema Evolution**: Versioned message formats enabling backward compatibility
6. **Performance Optimization**: High-throughput, low-latency messaging with batching and compression

### Mathematical Integration

The messaging layer maintains quantum-mechanical consistency:
- **Causal Ordering**: Messages preserve the causal structure of quantum state evolution
- **Energy Conservation**: State changes are validated to ensure energy function consistency
- **Lyapunov Monotonicity**: Message processing maintains Lyapunov potential non-increase
- **Closure Rule Compliance**: All state transitions via messages satisfy Δ closure rules

---

## 2. Core Infrastructure Files

### File: `messaging/__init__.py` (5 LOC)

**Purpose**: Package initializer exposing primary messaging interfaces and abstractions.

**Implementation**:
```python
"""
QuantaCirc Messaging Infrastructure
=================================

NATS JetStream-based messaging system providing asynchronous communication
for the agent ecosystem with quantum state consistency guarantees.
"""

from .nats_client import NATSClient
from .publisher import MessagePublisher
from .subscriber import MessageSubscriber
from .stream_manager import StreamManager

__all__ = ["NATSClient", "MessagePublisher", "MessageSubscriber", "StreamManager"]
```

**Integration Points**:
- Used by all agents for inter-agent communication
- Imported by core orchestrator for system coordination
- Referenced by monitoring systems for message observability

---

### File: `messaging/nats_client.py` (180 LOC)

**Purpose**: Core NATS JetStream client providing connection management, authentication, and quantum-aware messaging capabilities.

**Core Functionality**:
- NATS cluster connection with automatic failover
- JetStream context management for persistent messaging
- TLS encryption and authentication for secure communication
- Connection health monitoring and automatic reconnection
- Quantum state context propagation through message headers

**Implementation Strategy**:
```python
import asyncio
import nats
from nats.js import JetStreamContext
from typing import Dict, List, Optional, Callable, Any
import json
import logging
from dataclasses import dataclass
from datetime import datetime

from core.types import QCState, MessageMetadata
from .serialization import MessageSerializer

@dataclass
class NATSConfig:
    """Configuration for NATS connection."""
    servers: List[str]
    user: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    tls_cert: Optional[str] = None
    tls_key: Optional[str] = None
    max_reconnect_attempts: int = -1
    reconnect_time_wait: float = 2.0
    connect_timeout: float = 2.0

class NATSClient:
    """
    NATS JetStream client with quantum state awareness.
    
    Provides high-level interface for publishing and subscribing to messages
    while maintaining quantum mechanical consistency guarantees.
    """
    
    def __init__(self, config: NATSConfig):
        self.config = config
        self.connection: Optional[nats.NATS] = None
        self.jetstream: Optional[JetStreamContext] = None
        self.serializer = MessageSerializer()
        self.logger = logging.getLogger(__name__)
        self._is_connected = False
        self._connection_callbacks: List[Callable] = []
        self._disconnection_callbacks: List[Callable] = []
    
    async def connect(self) -> None:
        """Establish connection to NATS cluster with JetStream support."""
        try:
            # Configure connection options
            options = {
                "servers": self.config.servers,
                "max_reconnect_attempts": self.config.max_reconnect_attempts,
                "reconnect_time_wait": self.config.reconnect_time_wait,
                "connect_timeout": self.config.connect_timeout,
                "closed_cb": self._closed_callback,
                "reconnected_cb": self._reconnected_callback,
                "error_cb": self._error_callback
            }
            
            # Add authentication if provided
            if self.config.user and self.config.password:
                options["user"] = self.config.user
                options["password"] = self.config.password
            elif self.config.token:
                options["token"] = self.config.token
            
            # Add TLS configuration if provided
            if self.config.tls_cert and self.config.tls_key:
                options["tls"] = {
                    "cert": self.config.tls_cert,
                    "key": self.config.tls_key
                }
            
            # Establish connection
            self.connection = await nats.connect(**options)
            self.jetstream = self.connection.jetstream()
            self._is_connected = True
            
            self.logger.info("Connected to NATS cluster")
            
            # Notify connection callbacks
            for callback in self._connection_callbacks:
                try:
                    await callback()
                except Exception as e:
                    self.logger.error(f"Connection callback failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to connect to NATS: {e}")
            self._is_connected = False
            raise
    
    async def disconnect(self) -> None:
        """Gracefully disconnect from NATS cluster."""
        if self.connection:
            await self.connection.drain()
            await self.connection.close()
            self._is_connected = False
            self.logger.info("Disconnected from NATS cluster")
    
    async def publish_quantum_message(
        self,
        subject: str,
        message: Any,
        quantum_context: Optional[QCState] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Publish message with quantum state context propagation.
        
        Args:
            subject: NATS subject for message routing
            message: Message payload (will be serialized)
            quantum_context: Current quantum state for context propagation
            headers: Additional message headers
            
        Returns:
            Message ID for tracking and acknowledgment
        """
        if not self._is_connected or not self.jetstream:
            raise RuntimeError("Not connected to NATS")
        
        # Serialize message payload
        serialized_payload = self.serializer.serialize(message)
        
        # Prepare message headers
        msg_headers = headers or {}
        msg_headers["message-type"] = type(message).__name__
        msg_headers["timestamp"] = datetime.utcnow().isoformat()
        
        # Add quantum context to headers if provided
        if quantum_context:
            msg_headers.update(self._encode_quantum_context(quantum_context))
        
        try:
            # Publish message to JetStream
            ack = await self.jetstream.publish(
                subject=subject,
                payload=serialized_payload,
                headers=msg_headers
            )
            
            message_id = ack.seq
            self.logger.debug(f"Published message {message_id} to {subject}")
            return str(message_id)
            
        except Exception as e:
            self.logger.error(f"Failed to publish message to {subject}: {e}")
            raise
    
    async def subscribe_quantum_aware(
        self,
        subject: str,
        queue_group: Optional[str] = None,
        manual_ack: bool = True,
        max_deliver: int = 3
    ) -> 'QuantumAwareSubscription':
        """
        Create quantum-aware subscription with automatic context extraction.
        
        Returns subscription object that provides quantum context with each message.
        """
        if not self._is_connected or not self.jetstream:
            raise RuntimeError("Not connected to NATS")
        
        subscription = QuantumAwareSubscription(
            jetstream=self.jetstream,
            subject=subject,
            queue_group=queue_group,
            manual_ack=manual_ack,
            max_deliver=max_deliver,
            serializer=self.serializer,
            logger=self.logger
        )
        
        await subscription.start()
        return subscription
    
    def _encode_quantum_context(self, context: QCState) -> Dict[str, str]:
        """Encode quantum state context into message headers."""
        return {
            "qc-state-id": str(context.id),
            "qc-energy": str(context.energy),
            "qc-lyapunov": str(context.lyapunov_potential),
            "qc-phase": context.optimization_phase,
            "qc-timestamp": context.timestamp.isoformat()
        }
    
    def _decode_quantum_context(self, headers: Dict[str, str]) -> Optional[QCState]:
        """Decode quantum state context from message headers."""
        try:
            if "qc-state-id" in headers:
                # Reconstruct QCState from headers
                # This would typically involve fetching full state from persistence
                return QCState.from_headers(headers)
        except Exception as e:
            self.logger.warning(f"Failed to decode quantum context: {e}")
        return None
    
    async def _closed_callback(self) -> None:
        """Handle connection closure."""
        self._is_connected = False
        self.logger.warning("NATS connection closed")
        
        for callback in self._disconnection_callbacks:
            try:
                await callback()
            except Exception as e:
                self.logger.error(f"Disconnection callback failed: {e}")
    
    async def _reconnected_callback(self) -> None:
        """Handle successful reconnection."""
        self._is_connected = True
        self.logger.info("NATS connection reestablished")
        
        for callback in self._connection_callbacks:
            try:
                await callback()
            except Exception as e:
                self.logger.error(f"Reconnection callback failed: {e}")
    
    async def _error_callback(self, error: Exception) -> None:
        """Handle connection errors."""
        self.logger.error(f"NATS connection error: {error}")

class QuantumAwareSubscription:
    """Subscription wrapper providing quantum context extraction."""
    
    def __init__(self, jetstream, subject, queue_group, manual_ack, max_deliver, serializer, logger):
        self.jetstream = jetstream
        self.subject = subject
        self.queue_group = queue_group
        self.manual_ack = manual_ack
        self.max_deliver = max_deliver
        self.serializer = serializer
        self.logger = logger
        self.subscription = None
    
    async def start(self):
        """Start the subscription."""
        self.subscription = await self.jetstream.pull_subscribe(
            subject=self.subject,
            queue=self.queue_group,
            manual_ack=self.manual_ack,
            config=nats.js.api.ConsumerConfig(
                max_deliver=self.max_deliver,
                ack_policy=nats.js.api.AckPolicy.EXPLICIT if self.manual_ack else nats.js.api.AckPolicy.ALL
            )
        )
    
    async def next_message(self, timeout: float = 1.0) -> Optional['QuantumMessage']:
        """Get next message with quantum context extraction."""
        if not self.subscription:
            raise RuntimeError("Subscription not started")
        
        try:
            msgs = await self.subscription.fetch(batch=1, timeout=timeout)
            if msgs:
                raw_msg = msgs[0]
                return QuantumMessage(raw_msg, self.serializer, self.logger)
        except Exception as e:
            if "timeout" not in str(e).lower():
                self.logger.error(f"Error fetching message: {e}")
        
        return None

class QuantumMessage:
    """Message wrapper with quantum context extraction."""
    
    def __init__(self, raw_msg, serializer, logger):
        self.raw_msg = raw_msg
        self.serializer = serializer
        self.logger = logger
        self._payload = None
        self._quantum_context = None
    
    @property
    def payload(self):
        """Deserialize message payload on demand."""
        if self._payload is None:
            self._payload = self.serializer.deserialize(self.raw_msg.data)
        return self._payload
    
    @property
    def quantum_context(self) -> Optional[QCState]:
        """Extract quantum context from message headers."""
        if self._quantum_context is None and self.raw_msg.headers:
            self._quantum_context = self._decode_quantum_context(self.raw_msg.headers)
        return self._quantum_context
    
    async def ack(self):
        """Acknowledge message processing."""
        await self.raw_msg.ack()
    
    async def nak(self):
        """Negative acknowledge - requeue message."""
        await self.raw_msg.nak()
```

**Integration Points**:
- Used by all messaging components for NATS connectivity
- Integrates with quantum state management for context propagation
- Connects to monitoring systems for connection health tracking
- Provides foundation for publish/subscribe patterns

---

### File: `messaging/publisher.py` (80 LOC)

**Purpose**: High-level message publishing interface with batching, compression, and quantum state validation.

**Core Functionality**:
- Message batching for improved throughput
- Compression for large payloads
- Quantum state validation before publishing
- Retry logic with exponential backoff
- Message deduplication and idempotency

**Implementation Strategy**: Implements publisher patterns with quantum-aware validation ensuring all published messages maintain system consistency.

---

### File: `messaging/subscriber.py` (80 LOC)

**Purpose**: High-level message subscription interface with automatic message processing and error handling.

**Core Functionality**:
- Automatic message acknowledgment handling
- Dead letter queue integration for failed messages
- Concurrent message processing with worker pools
- Quantum state validation on received messages
- Circuit breaker pattern for failing consumers

**Implementation Strategy**: Robust subscription management with quantum consistency validation and fault tolerance.

---

### File: `messaging/stream_manager.py` (100 LOC)

**Purpose**: NATS stream lifecycle management with configuration, monitoring, and optimization.

**Core Functionality**:
- Stream creation and configuration management
- Consumer group management and scaling
- Message retention policy enforcement
- Stream replication and backup management
- Performance monitoring and optimization

**Implementation Strategy**: Comprehensive stream management ensuring high availability and performance for the quantum agent ecosystem.

---

### File: `messaging/topic_manager.py` (70 LOC)

**Purpose**: Topic schema management and routing configuration for organized message flow.

**Core Functionality**:
- Topic naming conventions and validation
- Schema registry integration for message formats
- Route optimization for message delivery
- Topic lifecycle management (creation, deprecation)
- Access control and authorization integration

**Implementation Strategy**: Centralized topic management ensuring consistent message routing and schema evolution.

---

### File: `messaging/serialization.py` (90 LOC)

**Purpose**: Message serialization and compression with versioning support for backward compatibility.

**Core Functionality**:
- Multiple serialization formats (JSON, MessagePack, Protobuf)
- Automatic compression for large messages
- Schema versioning and migration support
- Type-safe serialization with validation
- Performance optimization for high-throughput scenarios

**Implementation Strategy**:
```python
import json
import msgpack
import gzip
import lz4.frame
from typing import Any, Dict, Optional, Type
from dataclasses import is_dataclass, asdict
from enum import Enum
import pickle
from datetime import datetime
import uuid

class SerializationFormat(Enum):
    JSON = "json"
    MSGPACK = "msgpack"
    PICKLE = "pickle"

class CompressionType(Enum):
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"

class MessageSerializer:
    """
    High-performance message serializer with compression and versioning.
    
    Supports multiple formats and compression algorithms optimized
    for different message types and sizes.
    """
    
    def __init__(self, 
                 default_format: SerializationFormat = SerializationFormat.MSGPACK,
                 default_compression: CompressionType = CompressionType.LZ4,
                 compression_threshold: int = 1024):
        self.default_format = default_format
        self.default_compression = default_compression
        self.compression_threshold = compression_threshold
        
        # Register custom type handlers
        self._type_handlers = {
            datetime: self._serialize_datetime,
            uuid.UUID: str,
        }
        
        self._deserializers = {
            SerializationFormat.JSON: self._deserialize_json,
            SerializationFormat.MSGPACK: self._deserialize_msgpack,
            SerializationFormat.PICKLE: self._deserialize_pickle
        }
    
    def serialize(self, 
                  obj: Any, 
                  format: Optional[SerializationFormat] = None,
                  compression: Optional[CompressionType] = None) -> bytes:
        """
        Serialize object with optional compression.
        
        Args:
            obj: Object to serialize
            format: Serialization format (defaults to instance default)
            compression: Compression type (defaults to instance default)
            
        Returns:
            Serialized bytes with metadata header
        """
        format = format or self.default_format
        compression = compression or self.default_compression
        
        # Prepare object for serialization
        prepared_obj = self._prepare_object(obj)
        
        # Serialize based on format
        if format == SerializationFormat.JSON:
            serialized = json.dumps(prepared_obj, default=self._json_serializer).encode('utf-8')
        elif format == SerializationFormat.MSGPACK:
            serialized = msgpack.packb(prepared_obj, default=self._msgpack_serializer)
        elif format == SerializationFormat.PICKLE:
            serialized = pickle.dumps(prepared_obj)
        else:
            raise ValueError(f"Unsupported serialization format: {format}")
        
        # Apply compression if payload is large enough
        compressed = serialized
        actual_compression = CompressionType.NONE
        
        if len(serialized) > self.compression_threshold:
            if compression == CompressionType.GZIP:
                compressed = gzip.compress(serialized)
                actual_compression = CompressionType.GZIP
            elif compression == CompressionType.LZ4:
                compressed = lz4.frame.compress(serialized)
                actual_compression = CompressionType.LZ4
        
        # Create metadata header
        metadata = {
            "format": format.value,
            "compression": actual_compression.value,
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "original_size": len(serialized),
            "compressed_size": len(compressed)
        }
        
        # Combine metadata and payload
        metadata_bytes = json.dumps(metadata).encode('utf-8')
        metadata_length = len(metadata_bytes).to_bytes(4, byteorder='big')
        
        return metadata_length + metadata_bytes + compressed
    
    def deserialize(self, data: bytes) -> Any:
        """
        Deserialize bytes with automatic format and compression detection.
        
        Args:
            data: Serialized bytes with metadata header
            
        Returns:
            Deserialized object
        """
        if len(data) < 4:
            raise ValueError("Invalid serialized data: too short")
        
        # Extract metadata
        metadata_length = int.from_bytes(data[:4], byteorder='big')
        metadata_bytes = data[4:4+metadata_length]
        payload_bytes = data[4+metadata_length:]
        
        try:
            metadata = json.loads(metadata_bytes.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("Invalid metadata in serialized data")
        
        # Decompress if needed
        compression_type = CompressionType(metadata.get('compression', 'none'))
        
        if compression_type == CompressionType.GZIP:
            decompressed = gzip.decompress(payload_bytes)
        elif compression_type == CompressionType.LZ4:
            decompressed = lz4.frame.decompress(payload_bytes)
        else:
            decompressed = payload_bytes
        
        # Deserialize based on format
        format_type = SerializationFormat(metadata.get('format', 'msgpack'))
        deserializer = self._deserializers.get(format_type)
        
        if not deserializer:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return deserializer(decompressed)
    
    def _prepare_object(self, obj: Any) -> Any:
        """Prepare object for serialization by handling custom types."""
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._prepare_object(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._prepare_object(value) for key, value in obj.items()}
        elif is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, '__dict__'):
            return self._prepare_object(obj.__dict__)
        else:
            # Use registered type handlers
            for type_class, handler in self._type_handlers.items():
                if isinstance(obj, type_class):
                    return handler(obj)
            
            # Fallback to string representation
            return str(obj)
    
    def _serialize_datetime(self, dt: datetime) -> Dict[str, Any]:
        """Serialize datetime with type information."""
        return {
            "_type": "datetime",
            "_value": dt.isoformat()
        }
    
    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for special types."""
        if isinstance(obj, datetime):
            return self._serialize_datetime(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        else:
            return str(obj)
    
    def _msgpack_serializer(self, obj: Any) -> Any:
        """Custom MessagePack serializer for special types."""
        return self._json_serializer(obj)
    
    def _deserialize_json(self, data: bytes) -> Any:
        """Deserialize JSON data."""
        return json.loads(data.decode('utf-8'))
    
    def _deserialize_msgpack(self, data: bytes) -> Any:
        """Deserialize MessagePack data."""
        return msgpack.unpackb(data, raw=False)
    
    def _deserialize_pickle(self, data: bytes) -> Any:
        """Deserialize Pickle data."""
        return pickle.loads(data)
```

**Integration Points**:
- Used by all messaging components for data serialization
- Integrates with schema management for version control
- Optimizes performance through compression and format selection

---

## 3. Middleware Components (5 Files)

### File: `messaging/middleware/__init__.py` (5 LOC)

**Purpose**: Middleware package initializer exposing message processing middleware components.

**Implementation**:
```python
"""
Messaging Middleware Components
==============================

Pluggable middleware for message processing including logging,
metrics collection, validation, and retry logic.
"""

from .logging import LoggingMiddleware
from .metrics import MetricsMiddleware
from .retry import RetryMiddleware
from .validation import ValidationMiddleware

__all__ = ["LoggingMiddleware", "MetricsMiddleware", "RetryMiddleware", "ValidationMiddleware"]
```

---

### File: `messaging/middleware/logging.py` (60 LOC)

**Purpose**: Message logging middleware with structured logging and audit trail capabilities.

**Core Functionality**:
- Structured logging of all message events
- Audit trail generation for compliance
- Performance metrics logging
- Error event correlation
- Log level configuration per message type

**Implementation Strategy**: Comprehensive logging middleware providing full visibility into message processing with structured data for analysis.

---

### File: `messaging/middleware/metrics.py` (60 LOC)

**Purpose**: Prometheus metrics collection middleware for message processing observability.

**Core Functionality**:
- Message throughput and latency metrics
- Error rate and retry statistics
- Queue depth and backlog monitoring
- Consumer lag tracking
- Resource utilization metrics

**Implementation Strategy**: Real-time metrics collection enabling monitoring and alerting on messaging system performance.

---

### File: `messaging/middleware/retry.py` (70 LOC)

**Purpose**: Intelligent retry middleware with exponential backoff and dead letter queue integration.

**Core Functionality**:
- Configurable retry policies per message type
- Exponential backoff with jitter
- Dead letter queue routing for permanent failures
- Retry budget management to prevent infinite loops
- Circuit breaker integration for failing consumers

**Implementation Strategy**: Robust retry mechanisms ensuring message delivery while preventing system overload.

---

### File: `messaging/middleware/validation.py` (60 LOC)

**Purpose**: Message validation middleware ensuring data integrity and quantum state consistency.

**Core Functionality**:
- Schema validation for message payloads
- Quantum state consistency checking
- Business rule validation
- Input sanitization and security checks
- Performance-optimized validation caching

**Implementation Strategy**: Multi-layered validation ensuring all messages meet quality and consistency requirements before processing.

---

## 4. Integration Architecture

### Quantum State Consistency
The messaging system maintains quantum mechanical principles:
- **Causal Message Ordering**: Preserves the causal structure of quantum evolution
- **State Transition Validation**: Ensures all messages maintain energy conservation
- **Lyapunov Monotonicity**: Message processing preserves stability properties
- **Closure Rule Enforcement**: All state changes satisfy formal constraints

### Performance Optimization
High-performance messaging through:
- **Batching and Compression**: Optimizes throughput for large message volumes
- **Connection Pooling**: Efficient resource utilization across components
- **Async Processing**: Non-blocking message handling with coroutine optimization
- **Load Balancing**: Intelligent message routing and consumer scaling

### Fault Tolerance
Robust error handling and recovery:
- **Message Persistence**: Guaranteed delivery through JetStream persistence
- **Automatic Retry**: Intelligent retry with exponential backoff
- **Dead Letter Queues**: Isolation of permanently failed messages
- **Circuit Breakers**: Protection against cascading failures

### Security and Compliance
Enterprise-grade security features:
- **TLS Encryption**: End-to-end message encryption
- **Authentication**: Token and certificate-based authentication
- **Authorization**: Fine-grained access control per topic
- **Audit Trails**: Complete message processing history

This comprehensive messaging infrastructure provides the communication backbone for QuantaCirc's distributed agent ecosystem while maintaining quantum-mechanical consistency and providing enterprise-grade reliability and performance.
