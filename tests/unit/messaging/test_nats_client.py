"""
Comprehensive Tests for NATS Client
Mathematical Foundation: Message delivery guarantees, ordering preservation
Physics Principle: Information propagation, causal ordering
What Gets Tested: NATS integration, context propagation, reliability
Failure Analysis: Diagnostic guidance for NATS connection, authentication, and configuration issues
"""

import pytest
from tests.conftest import TestDiagnostic
import asyncio
from unittest.mock import AsyncMock, patch, PropertyMock, MagicMock
from uuid import uuid4
from core.data_models import QCState, SoftwareState, EnergyBreakdown, LyapunovMetrics
from nats.aio.msg import Msg

from messaging.nats_client import NATSClient

class TestNatsClient:
    def test_nats_client_import(self):
        diagnostic = TestDiagnostic(
            component_name="NATS Client",
            expected_behavior="The NATS client module should be importable.",
            failure_indicators=["ImportError"],
            build_instructions=["Create the NATS client in 'messaging/nats_client.py'"],
            mathematical_requirements=["Guaranteed delivery (P(delivery) = 1)"],
            acceptance_criteria={"import": "successful"},
            physics_principle="Causal information propagation",
            related_components=["Publisher", "Subscriber", "StreamManager"]
        )
        try:
            from messaging.nats_client import NATSClient as NatsClient
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))

@pytest.mark.asyncio
async def test_nats_client_connect_disconnect():
    """
    Tests that the NATS client can connect and disconnect successfully.
    """
    mock_nats_client = AsyncMock()
    type(mock_nats_client).is_connected = PropertyMock(return_value=True)
    type(mock_nats_client).is_closed = PropertyMock(return_value=False)
    mock_nats_client.connected_url.netloc = "mock-server"

    with patch('nats.connect', new=AsyncMock(return_value=mock_nats_client)) as mock_connect:
        client = NATSClient(server_urls="nats://localhost:4222")
        await client.connect()

        assert client.nc is not None
        assert client.js is not None
        assert client._is_connected is True
        mock_connect.assert_called_once()

        await client.disconnect()
        assert client._is_connected is False
        mock_nats_client.close.assert_called_once()

@pytest.mark.asyncio
async def test_publish_with_quantum_context():
    """
    Tests that publishing a message correctly encodes and sends the quantum context.
    """
    mock_nats_client = AsyncMock()
    mock_js_context = AsyncMock()
    from unittest.mock import MagicMock
    mock_nats_client.jetstream = MagicMock(return_value=mock_js_context)

    with patch('nats.connect', new=AsyncMock(return_value=mock_nats_client)):
        client = NATSClient(server_urls="nats://localhost:4222")
        await client.connect()

        energy_breakdown = EnergyBreakdown(total=1.0, complexity=1.0, coupling=0.0, constraint=0.0, debt=0.0)
        lyapunov_metrics = LyapunovMetrics(phi=1.0, energy=1.0, test_penalty=0.0, obligation_penalty=0.0)
        qc_state = QCState(
            id=uuid4(),
            software_state=SoftwareState(component_versions={}, config_hashes={}),
            energy_breakdown=energy_breakdown,
            lyapunov_metrics=lyapunov_metrics,
            contraction_factor=0.5
        )
        payload = b"test_payload"
        subject = "test.subject"

        with patch.object(client, '_encode_quantum_context', wraps=client._encode_quantum_context) as spy_encode:
            await client.publish_quantum_message(subject, payload, qc_state)

            spy_encode.assert_called_once_with(qc_state)

            # Check that js.publish was called with the encoded context in headers
            args, kwargs = mock_js_context.publish.call_args
            assert args[0] == subject
            assert args[1] == payload
            assert "headers" in kwargs
            assert "X-Quantum-Context" in kwargs["headers"]

@pytest.mark.asyncio
async def test_subscribe_and_receive_message():
    """
    Tests that subscribing to a topic correctly receives and decodes a message
    with a quantum context.
    """
    mock_nats_client = AsyncMock()
    mock_js_context = AsyncMock()
    from unittest.mock import MagicMock
    mock_nats_client.jetstream = MagicMock(return_value=mock_js_context)

    with patch('nats.connect', new=AsyncMock(return_value=mock_nats_client)):
        client = NATSClient(server_urls="nats://localhost:4222")
        await client.connect()

        energy_breakdown = EnergyBreakdown(total=1.0, complexity=1.0, coupling=0.0, constraint=0.0, debt=0.0)
        lyapunov_metrics = LyapunovMetrics(phi=1.0, energy=1.0, test_penalty=0.0, obligation_penalty=0.0)
        qc_state = QCState(
            id=uuid4(),
            software_state=SoftwareState(component_versions={}, config_hashes={}),
            energy_breakdown=energy_breakdown,
            lyapunov_metrics=lyapunov_metrics,
            contraction_factor=0.5
        )

        # Manually create a message with encoded context
        encoded_context = client._encode_quantum_context(qc_state)
        test_msg = Msg(
            _client=None,
            subject='test.subject',
            reply='',
            data=b'test data',
            headers=encoded_context
        )

        # This queue will be used to assert that the callback was called
        received_queue = asyncio.Queue()

        async def my_callback(msg, context):
            await received_queue.put((msg, context))

        # Mock the internal subscribe call to immediately call our wrapped_callback
        # with the test message.
        async def mock_subscribe(*args, **kwargs):
            cb = kwargs.get('cb')
            assert cb is not None, "Callback was not provided to subscribe"
            # In a real scenario, the NATS server would invoke this.
            # Here, we invoke it directly to simulate a received message.
            await cb(test_msg)

        mock_js_context.subscribe = AsyncMock(side_effect=mock_subscribe)

        await client.subscribe_quantum_aware(
            subject="test.subject",
            callback=my_callback,
            stream="test_stream" # Required for js.subscribe
        )

        # Verify that the callback was called and the context was decoded
        received_msg, received_context = await asyncio.wait_for(received_queue.get(), timeout=1.0)

        assert received_msg.data == test_msg.data
        assert received_context is not None
        assert received_context.id == qc_state.id
        assert received_context.energy == qc_state.energy
