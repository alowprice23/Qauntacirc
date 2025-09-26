import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from core.state_manager import StateManager, StateChangeEvent
from core.system_state import SystemState

class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.nats_client = MagicMock()
        self.nats_client.publish = AsyncMock()
        self.nats_client.subscribe = AsyncMock()

        self.state_manager = StateManager(self.nats_client)

    def test_publish_state_change(self):
        agent_name = "test_agent"
        delta = {"key": "value"}
        event = StateChangeEvent(agent_name=agent_name, delta=delta)

        self.loop.run_until_complete(
            self.state_manager.publish_state_change(agent_name, delta)
        )

        self.nats_client.publish.assert_called_once_with(
            f"{self.state_manager.stream_name}.{agent_name}",
            event.model_dump_json().encode()
        )

    @patch('asyncio.sleep', new_callable=AsyncMock)
    def test_get_current_state(self, mock_sleep):
        initial_state = SystemState()

        # Mock the subscription and messages
        mock_sub = MagicMock()

        # Create mock messages
        event1 = StateChangeEvent(agent_name="agent1", delta={"data1": "value1"})
        msg1 = MagicMock()
        msg1.data = event1.model_dump_json().encode()

        event2 = StateChangeEvent(agent_name="agent2", delta={"data2": "value2"})
        msg2 = MagicMock()
        msg2.data = event2.model_dump_json().encode()

        # Set up the async iterator for next_msg
        async def mock_next_msg_generator():
            yield msg1
            yield msg2
            raise asyncio.TimeoutError # to break the loop

        mock_sub.next_msg = AsyncMock(side_effect=mock_next_msg_generator())
        self.nats_client.subscribe.return_value = mock_sub

        # Run the method
        final_state = self.loop.run_until_complete(
            self.state_manager.get_current_state(initial_state)
        )

        # Check assertions
        self.assertIn("data1", final_state.data)
        self.assertEqual(final_state.data["data1"], "value1")
        self.assertIn("data2", final_state.data)
        self.assertEqual(final_state.data["data2"], "value2")

    def tearDown(self):
        self.loop.close()

if __name__ == '__main__':
    unittest.main()