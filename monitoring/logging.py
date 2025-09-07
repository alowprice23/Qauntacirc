# monitoring/logging.py

import logging
import json
from opentelemetry import trace

class JSONFormatter(logging.Formatter):
    """
    Custom logging formatter to output log records as JSON strings.
    This formatter automatically includes trace and span IDs from OpenTelemetry
    if a trace is active, enabling log correlation in distributed systems.
    """
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
        }

        # Add correlation IDs from the active OpenTelemetry trace context
        span = trace.get_current_span()
        if span.is_recording():
            ctx = span.get_span_context()
            log_record["trace_id"] = f"{ctx.trace_id:032x}"
            log_record["span_id"] = f"{ctx.span_id:016x}"

        # Add extra fields passed to the logger
        if hasattr(record, 'extra_info'):
            log_record.update(record.extra_info)

        return json.dumps(log_record)

class StructuredLogger:
    """
    A structured logger for the quantum simulation platform. It integrates
    quantum context and correlation IDs into logs, and outputs in JSON format
    for easy parsing and aggregation by centralized logging systems.
    """
    def __init__(self, name="quantum_logger", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # Avoid duplicate logs in parent loggers

        # Configure a handler with the JSON formatter if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()  # In production, use an async handler
            formatter = JSONFormatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log(self, level, msg, quantum_context=None, **kwargs):
        extra = {"extra_info": kwargs}
        if quantum_context:
            extra["extra_info"]["quantum_context"] = quantum_context

        self.logger.log(level, msg, extra=extra)

    def info(self, msg, quantum_context=None, **kwargs):
        """Logs a message with INFO level."""
        self._log(logging.INFO, msg, quantum_context, **kwargs)

    def warning(self, msg, quantum_context=None, **kwargs):
        """Logs a message with WARNING level."""
        self._log(logging.WARNING, msg, quantum_context, **kwargs)

    def error(self, msg, quantum_context=None, **kwargs):
        """Logs a message with ERROR level."""
        self._log(logging.ERROR, msg, quantum_context, **kwargs)

    def critical(self, msg, quantum_context=None, **kwargs):
        """Logs a message with CRITICAL level."""
        self._log(logging.CRITICAL, msg, quantum_context, **kwargs)

    def debug(self, msg, quantum_context=None, **kwargs):
        """Logs a message with DEBUG level."""
        self._log(logging.DEBUG, msg, quantum_context, **kwargs)
