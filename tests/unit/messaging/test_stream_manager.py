"""
Comprehensive Tests for Stream Manager
Mathematical Foundation: Stream capacity, throughput optimization
Physics Principle: Flow dynamics, stream optimization
What Gets Tested: Stream management, performance optimization
Failure Analysis: Diagnostic guidance for stream creation and configuration failures
"""

import pytest
from tests.conftest import TestDiagnostic
import asyncio
from unittest.mock import AsyncMock, MagicMock
from nats.js.api import StreamConfig
from nats.js.errors import APIError

from messaging.stream_manager import StreamManager
from messaging.nats_client import NATSMessageBus

class TestStreamManager:
    def test_stream_manager_import(self):
        diagnostic = TestDiagnostic(
            component_name="StreamManager",
            expected_behavior="The StreamManager module should be importable.",
            failure_indicators=["ImportError"],
            build_instructions=["Create the StreamManager in 'messaging/stream_manager.py'"],
            mathematical_requirements=["Throughput optimization subject to capacity constraints"],
            acceptance_criteria={"import": "successful"},
            physics_principle="Flow dynamics and optimization",
            related_components=["NatsClient", "TopicManager"]
        )
        try:
            from messaging.stream_manager import StreamManager
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))

@pytest.mark.asyncio
async def test_create_new_stream():
    """
    Tests creating a new stream when it doesn't exist.
    """
    mock_nats_client = AsyncMock(spec=NATSMessageBus)
    mock_js_context = AsyncMock()
    # Simulate stream not found error, then success on add
    mock_js_context.update_stream.side_effect = APIError(err_code=10059)
    mock_js_context.add_stream = AsyncMock()

    # This is a bit tricky, we need to mock the _get_jsm method to return our mock_js_context
    async def get_jsm():
        return mock_js_context

    manager = StreamManager(nats_client=mock_nats_client)
    manager._get_jsm = get_jsm

    stream_name = "new-stream"
    subjects = ["new.subject.*"]

    await manager.create_or_update_stream(stream_name=stream_name, subjects=subjects)

    mock_js_context.add_stream.assert_called_once()
    args, kwargs = mock_js_context.add_stream.call_args
    config = args[0]
    assert isinstance(config, StreamConfig)
    assert config.name == stream_name
    assert config.subjects == subjects

@pytest.mark.asyncio
async def test_update_existing_stream():
    """
    Tests updating an existing stream.
    """
    mock_nats_client = AsyncMock(spec=NATSMessageBus)
    mock_js_context = AsyncMock()
    mock_js_context.update_stream = AsyncMock()

    async def get_jsm():
        return mock_js_context

    manager = StreamManager(nats_client=mock_nats_client)
    manager._get_jsm = get_jsm

    stream_name = "existing-stream"
    config = StreamConfig(name=stream_name, subjects=["foo", "bar"])

    await manager.create_or_update_stream(stream_name=stream_name, config=config)

    mock_js_context.update_stream.assert_called_once_with(config)
