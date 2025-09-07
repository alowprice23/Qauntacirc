# messaging/middleware/logging.py

"""
Middleware for structured logging of messaging events.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from nats.aio.msg import Msg
from core.types import QCState

# Use structlog if available for better structured logging, otherwise use standard logging.
try:
    import structlog
    log = structlog.get_logger(__name__)
    STRUCTLOG_AVAILABLE = True
except ImportError:
    log = logging.getLogger(__name__)
    STRUCTLOG_AVAILABLE = False


class LoggingMiddleware:
    """
    Provides a set of methods for structured logging of messaging events,
    creating an audit trail and capturing performance metrics.
    """

    @staticmethod
    def _log(event: str, **kwargs):
        """Helper to log with structlog if available, otherwise format a string."""
        if STRUCTLOG_AVAILABLE:
            log.info(event, **kwargs)
        else:
            # Basic fallback if structlog is not used
            message = f"event='{event}'"
            for k, v in kwargs.items():
                message += f" {k}='{v}'"
            log.info(message)

    @classmethod
    def log_publication(
        cls,
        subject: str,
        message_id: str,
        payload_size: int,
        is_compressed: bool,
        quantum_context: Optional[QCState] = None,
        trace_id: Optional[str] = None,
    ):
        """Logs the event of a message being published."""
        log_data = {
            "subject": subject,
            "message_id": message_id,
            "payload_size_bytes": payload_size,
            "is_compressed": is_compressed,
            "quantum_context_id": str(quantum_context.id) if quantum_context else None,
            "trace_id": trace_id,
            "direction": "outbound",
        }
        cls._log("message_published", **log_data)

    @classmethod
    def log_reception(cls, msg: Msg, quantum_context: Optional[QCState] = None):
        """Logs the event of a message being received."""
        headers = msg.headers or {}
        message_id = headers.get("Nats-Msg-Id")
        trace_id = headers.get("X-Trace-Id")

        log_data = {
            "subject": msg.subject,
            "reply_subject": msg.reply,
            "message_id": message_id,
            "payload_size_bytes": len(msg.data),
            "num_delivered": msg.metadata.num_delivered,
            "quantum_context_id": str(quantum_context.id) if quantum_context else None,
            "trace_id": trace_id,
            "direction": "inbound",
        }
        cls._log("message_received", **log_data)

    @classmethod
    def log_processing_result(
        cls,
        msg: Msg,
        duration_ms: float,
        success: bool,
        error: Optional[Exception] = None,
    ):
        """
        Logs the result of message processing, including performance metrics.
        """
        headers = msg.headers or {}
        message_id = headers.get("Nats-Msg-Id")

        log_data = {
            "subject": msg.subject,
            "message_id": message_id,
            "processing_duration_ms": round(duration_ms, 2),
            "success": success,
        }
        if error:
            log_data["error_type"] = type(error).__name__
            log_data["error_message"] = str(error)

        cls._log("message_processed", **log_data)

    @classmethod
    def log_dlq_event(cls, msg: Msg, reason: str, dlq_subject: str):
        """Logs the event of a message being sent to the Dead Letter Queue."""
        headers = msg.headers or {}
        message_id = headers.get("Nats-Msg-Id")

        log_data = {
            "subject": msg.subject,
            "message_id": message_id,
            "dlq_reason": reason,
            "dlq_subject": dlq_subject,
        }
        cls._log("message_dlq", **log_data)

    @classmethod
    def log_circuit_breaker_state_change(cls, subject: str, state: str):
        """Logs a change in the state of a circuit breaker."""
        log_data = {
            "subject": subject,
            "circuit_breaker_state": state,
        }
        cls._log("circuit_breaker_state_changed", **log_data)
