"""
Comprehensive Tests for Message Publisher
Mathematical Foundation: Batch optimization, compression ratios
Physics Principle: Information transmission optimization
What Gets Tested: Publishing reliability, optimization effectiveness
Failure Analysis: Diagnostic guidance for message publishing failures
"""

import pytest
from tests.conftest import TestDiagnostic
import asyncio
from unittest.mock import AsyncMock, MagicMock
from pydantic import BaseModel

from messaging.publisher import MessagePublisher
from messaging.nats_client import NATSClient
from messaging.serialization import MessageSerializer, SerializationFormat

class TestPublisher:
    def test_publisher_import(self):
        diagnostic = TestDiagnostic(
            component_name="Publisher",
            expected_behavior="The Publisher module should be importable.",
            failure_indicators=["ImportError"],
            build_instructions=["Create the Publisher in 'messaging/publisher.py'"],
            mathematical_requirements=["Batch optimization to minimize overhead"],
            acceptance_criteria={"import": "successful"},
            physics_principle="Information transmission optimization",
            related_components=["NatsClient", "Serialization"]
        )
        try:
            from messaging.publisher import MessagePublisher as Publisher
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))

class DummyModel(BaseModel):
    message: str

@pytest.mark.asyncio
async def test_publish_single_message():
    """
    Tests that the publish method correctly serializes and publishes a single message.
    """
    mock_nats_client = AsyncMock(spec=NATSClient)
    mock_serializer = MagicMock(spec=MessageSerializer)

    publisher = MessagePublisher(nats_client=mock_nats_client, serializer=mock_serializer)

    test_data = DummyModel(message="hello")
    test_subject = "test.subject"

    # Configure the mock serializer to return a dummy payload
    mock_serializer.serialize.return_value = (b'{"message": "hello"}', False)

    message_id = await publisher.publish(test_subject, test_data)

    # Verify that the serializer was called correctly
    mock_serializer.serialize.assert_called_once_with(test_data, format=SerializationFormat.JSON)

    # Verify that the NATS client was called to publish
    mock_nats_client.publish_quantum_message.assert_called_once()
    args, kwargs = mock_nats_client.publish_quantum_message.call_args

    assert kwargs['subject'] == test_subject
    assert kwargs['payload'] == b'{"message": "hello"}'
    assert "Nats-Msg-Id" in kwargs['headers']
    assert kwargs['headers']['Nats-Msg-Id'] == message_id
