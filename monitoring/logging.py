import logging
import json
from typing import Optional, Dict, Any

class StructuredLogger:
    """
    High-performance structured logging with quantum context integration.
    """
    def __init__(self, name: str, level: int = logging.INFO, correlation_id: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.correlation_id = correlation_id

        # Prevent duplicate handlers if logger is already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = JsonFormatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None):
        """Base logging method."""
        log_record = {
            "message": message,
            "correlation_id": self.correlation_id,
        }
        if extra:
            log_record.update(extra)

        self.logger.log(level, log_record)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.INFO, message, extra)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.DEBUG, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.WARNING, message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=False):
        self._log(logging.ERROR, message, extra)
        if exc_info:
            self.logger.exception(message)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.CRITICAL, message, extra)

    def set_correlation_id(self, correlation_id: str):
        self.correlation_id = correlation_id


class JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON strings.
    """
    def format(self, record):
        log_object = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
        }

        if isinstance(record.msg, dict):
            log_object.update(record.msg)
        else:
            log_object["message"] = record.getMessage()

        if record.exc_info:
            log_object['exc_info'] = self.formatException(record.exc_info)

        return json.dumps(log_object)

def setup_logging(level: str = "INFO"):
    """
    Configures the root logger for structured JSON logging.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add our custom JSON formatter
    handler = logging.StreamHandler()
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Suppress verbose logging from other libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)