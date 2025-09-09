import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from pydantic import BaseModel

from core.exceptions import MessagingError, QuantumStateError
from core.types import QCState, SoftwareState, EnergyComponents
from messaging.publisher import MessagePublisher
from messaging.nats_client import NATSClient
from messaging.serialization import MessageSerializer, SerializationFormat

class MockData(BaseModel):
    message: str

def create_valid_qc_state():
    """Helper function to create a valid QCState object for tests."""
    return QCState(
        id=uuid4(),
        software_state=SoftwareState(
            component_versions={"test_component": "1.0"},
            config_hashes={"test_config": "abc"},
            status="nominal"
        ),
        energy=1.0,
        energy_components=EnergyComponents(static=0.5, dynamic=0.3, interaction=0.2),
        lyapunov_potential=0.1,
        contraction_factor=0.9
    )

@pytest.fixture
def mock_nats_client():
    return AsyncMock(spec=NATSClient)

@pytest.fixture
def mock_serializer():
    serializer = MagicMock(spec=MessageSerializer)
    serializer.serialize.return_value = (b'{"message": "hello"}', False)
    return serializer

@pytest.fixture
def publisher(mock_nats_client, mock_serializer):
    return MessagePublisher(
        nats_client=mock_nats_client,
        serializer=mock_serializer,
        max_retries=3,
        retry_delay_base=0.01  # Use a small delay for tests
    )

@pytest.mark.asyncio
async def test_publish_successful(publisher, mock_nats_client):
    """Test a successful message publish on the first attempt."""
    data = MockData(message="hello")
    message_id = await publisher.publish("test.subject", data)

    assert isinstance(message_id, str)
    mock_nats_client.publish_quantum_message.assert_called_once()
    args, kwargs = mock_nats_client.publish_quantum_message.call_args
    assert kwargs["subject"] == "test.subject"
    assert kwargs["payload"] == b'{"message": "hello"}'

@pytest.mark.asyncio
async def test_publish_with_retry(publisher, mock_nats_client):
    """Test that the publisher retries on failure and succeeds."""
    mock_nats_client.publish_quantum_message.side_effect = [
        MessagingError("Failed to connect"),
        MessagingError("Still failing"),
        None  # Success on the third attempt
    ]

    data = MockData(message="hello")
    await publisher.publish("test.subject", data)

    assert mock_nats_client.publish_quantum_message.call_count == 3

@pytest.mark.asyncio
async def test_publish_fails_after_retries(publisher, mock_nats_client):
    """Test that publishing raises an error after all retries are exhausted."""
    mock_nats_client.publish_quantum_message.side_effect = MessagingError("Persistent failure")

    with pytest.raises(MessagingError):
        await publisher.publish("test.subject", MockData(message="hello"))

    assert mock_nats_client.publish_quantum_message.call_count == 3

@pytest.mark.asyncio
async def test_publish_invalid_quantum_state(publisher):
    """Test that publishing with an invalid quantum state raises an error."""
    # Mock QCState to fail validation
    with patch('core.types.QCState.model_validate', side_effect=ValueError("Invalid state")):
        with pytest.raises(QuantumStateError):
            await publisher.publish(
                "test.subject",
                MockData(message="hello"),
                quantum_context=create_valid_qc_state()
            )

@pytest.mark.asyncio
async def test_publish_batch_successful(publisher, mock_nats_client):
    """Test publishing a batch of messages successfully."""
    messages = [
        (MockData(message="msg1"), None),
        (MockData(message="msg2"), create_valid_qc_state()),
    ]

    message_ids = await publisher.publish_batch("test.batch", messages)

    assert len(message_ids) == 2
    assert mock_nats_client.publish_quantum_message.call_count == 2

@pytest.mark.asyncio
async def test_publish_batch_partial_failure(publisher, mock_nats_client):
    """Test a batch publish where some messages fail."""

    async def side_effect(*args, **kwargs):
        if mock_nats_client.publish_quantum_message.call_count == 1:
            return "id-1"
        else:
            raise MessagingError("Failed to publish second message")

    mock_nats_client.publish_quantum_message.side_effect = side_effect

    messages = [
        (MockData(message="msg1"), None),
        (MockData(message="msg2"), None),
    ]

    with pytest.raises(MessagingError, match="Only 1/2 messages were published successfully"):
        await publisher.publish_batch("test.batch", messages)

    # 1 successful call + 3 retries for the second message
    assert mock_nats_client.publish_quantum_message.call_count == 1 + 3
