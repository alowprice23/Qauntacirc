"""
Comprehensive Tests for Messaging Middleware
Mathematical Foundation: Pipeline composition, filter mathematics
Physics Principle: Signal processing, filter theory
What Gets Tested: Middleware correctness, pipeline integrity
Failure Analysis: Diagnostic guidance for middleware processing failures
"""

import pytest
from tests.conftest import TestDiagnostic
from unittest.mock import MagicMock, patch
from pydantic import BaseModel

from messaging.middleware.logging import LoggingMiddleware
from messaging.middleware.validation import ValidationMiddleware
from messaging.topic_manager import TopicManager
from core.exceptions import SchemaValidationError

class TestMiddleware:
    def test_middleware_import(self):
        diagnostic = TestDiagnostic(
            component_name="Middleware",
            expected_behavior="The Middleware module should be importable.",
            failure_indicators=["ImportError"],
            build_instructions=["Create the Middleware in 'messaging/middleware.py'"],
            mathematical_requirements=["Function composition for pipeline"],
            acceptance_criteria={"import": "successful"},
            physics_principle="Signal processing and filter theory",
            related_components=["Publisher", "Subscriber"]
        )
        try:
            from messaging.middleware.logging import LoggingMiddleware
            from messaging.middleware.validation import ValidationMiddleware
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))

class DummySchema(BaseModel):
    field: str

@patch('messaging.middleware.logging.STRUCTLOG_AVAILABLE', True)
@patch('messaging.middleware.logging.log')
def test_logging_middleware_log_publication(mock_log):
    """
    Tests that the LoggingMiddleware correctly logs a publication event.
    """
    LoggingMiddleware.log_publication(
        subject="test.subject",
        message_id="123",
        payload_size=100,
        is_compressed=False
    )
    mock_log.info.assert_called_once_with(
        "message_published",
        subject="test.subject",
        message_id="123",
        payload_size_bytes=100,
        is_compressed=False,
        quantum_context_id=None,
        trace_id=None,
        direction="outbound"
    )

def test_validation_middleware_success():
    """
    Tests that the ValidationMiddleware successfully validates a correct payload.
    """
    mock_topic_manager = MagicMock(spec=TopicManager)
    mock_topic_manager.get_schema_for_topic.return_value = DummySchema

    validator = ValidationMiddleware(topic_manager=mock_topic_manager)

    payload = DummySchema(field="test")

    # This should not raise an exception
    validator.validate_payload_schema("test.subject", payload)
    mock_topic_manager.get_schema_for_topic.assert_called_once_with("test.subject")

def test_validation_middleware_failure():
    """
    Tests that the ValidationMiddleware raises an error for an incorrect payload.
    """
    mock_topic_manager = MagicMock(spec=TopicManager)
    mock_topic_manager.get_schema_for_topic.return_value = DummySchema

    validator = ValidationMiddleware(topic_manager=mock_topic_manager)

    class AnotherSchema(BaseModel):
        another_field: int

    payload = AnotherSchema(another_field=123)

    with pytest.raises(SchemaValidationError):
        validator.validate_payload_schema("test.subject", payload)
