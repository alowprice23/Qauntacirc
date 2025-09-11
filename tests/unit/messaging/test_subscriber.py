"""
Comprehensive Tests for Message Subscriber
Mathematical Foundation: Acknowledgment protocols, delivery confirmation
Physics Principle: Information reception, feedback control
What Gets Tested: Subscription reliability, acknowledgment handling
Failure Analysis: Diagnostic guidance for message subscription failures
"""

import pytest
from tests.conftest import TestDiagnostic
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel
from nats.aio.msg import Msg

from messaging.subscriber import MessageSubscriber
from messaging.nats_client import NATSClient
from messaging.serialization import MessageSerializer, SerializationFormat

class TestSubscriber:
    def test_subscriber_import(self):
        diagnostic = TestDiagnostic(
            component_name="Subscriber",
            expected_behavior="The Subscriber module should be importable.",
            failure_indicators=["ImportError"],
            build_instructions=["Create the Subscriber in 'messaging/subscriber.py'"],
            mathematical_requirements=["Acknowledgment to confirm delivery"],
            acceptance_criteria={"import": "successful"},
            physics_principle="Information reception and feedback control",
            related_components=["NatsClient", "Serialization"]
        )
        try:
            from messaging.subscriber import MessageSubscriber as Subscriber
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))

class DummyModel(BaseModel):
    message: str

@pytest.mark.asyncio
async def test_subscriber_receives_message():
    """
    Tests that the subscriber correctly deserializes and processes a received message.
    """
    mock_nats_client = AsyncMock(spec=NATSClient)
    mock_serializer = MagicMock(spec=MessageSerializer)

    subscriber = MessageSubscriber(nats_client=mock_nats_client, serializer=mock_serializer)

    test_data = DummyModel(message="hello")
    deserialized_data = DummyModel(message="hello")

    # Configure the mock serializer
    mock_serializer.deserialize.return_value = deserialized_data

    # This queue will be used to assert that the callback was called
    received_queue = asyncio.Queue()
    async def user_callback(data, context):
        await received_queue.put((data, context))

    # Mock the subscribe_quantum_aware method to simulate a message reception
    async def mock_subscribe_quantum_aware(subject, callback, **kwargs):
        # In a real scenario, the NATS client would call the wrapped_callback.
        # We simulate this by creating a test message and calling the callback.
        test_msg = Msg(
            _client=None,
            subject=subject,
            reply='',
            data=b'{"message": "hello"}',
            headers={
                "X-Serialization-Format": "json",
                "X-Payload-Compressed": "false",
                "Nats-Msg-Id": "123"
            }
        )
        test_msg.ack = AsyncMock()
        with patch('nats.aio.msg.Msg.metadata', new_callable=MagicMock) as mock_metadata:
            mock_metadata.num_delivered = 1
            # The 'callback' passed to subscribe_quantum_aware is the wrapper
            await callback(test_msg, None)

    mock_nats_client.subscribe_quantum_aware = AsyncMock(side_effect=mock_subscribe_quantum_aware)

    await subscriber.subscribe(
        subject="test.subject",
        target_class=DummyModel,
        callback=user_callback
    )

    # Check that subscribe_quantum_aware was called
    mock_nats_client.subscribe_quantum_aware.assert_called_once()

    # Verify that the user callback was called with the correct data
    received_data, received_context = await asyncio.wait_for(received_queue.get(), timeout=1.0)

    assert received_data == deserialized_data
    mock_serializer.deserialize.assert_called_once()
