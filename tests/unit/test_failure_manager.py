import unittest
from unittest.mock import MagicMock

from core.failure_manager import FailureManager, RecoveryStrategy
from core.rollback_manager import RollbackManager
from core.system_state import SystemState

class TestFailureManager(unittest.TestCase):
    def setUp(self):
        self.rollback_manager = MagicMock(spec=RollbackManager)
        self.failure_manager = FailureManager(self.rollback_manager)

    def test_handle_failure_continue_strategy(self):
        agent_name = "test_agent"
        exception = Exception("Test exception")
        initial_state = SystemState(data={"key": "original"})
        self.rollback_manager.rollback.return_value = initial_state

        state = self.failure_manager.handle_failure(
            agent_name, exception, RecoveryStrategy.CONTINUE
        )

        self.rollback_manager.rollback.assert_called_once_with(agent_name)
        self.assertEqual(state, initial_state)
        self.assertEqual(self.failure_manager.agent_failure_counts[agent_name], 1)

    def test_handle_failure_retry_strategy_success(self):
        agent_name = "test_agent_retry"
        exception = Exception("Test exception")
        initial_state = SystemState(data={"key": "rolled_back"})
        self.rollback_manager.rollback.return_value = initial_state

        # First failure
        state = self.failure_manager.handle_failure(
            agent_name, exception, RecoveryStrategy.RETRY, max_retries=3
        )
        self.rollback_manager.rollback.assert_called_with(agent_name)
        self.assertEqual(self.failure_manager.agent_failure_counts[agent_name], 1)
        self.assertEqual(state, initial_state)

        # Second failure (still within retry limit)
        state = self.failure_manager.handle_failure(
            agent_name, exception, RecoveryStrategy.RETRY, max_retries=3
        )
        self.assertEqual(self.failure_manager.agent_failure_counts[agent_name], 2)
        self.assertEqual(state, initial_state)

    def test_handle_failure_retry_strategy_exceeded(self):
        agent_name = "test_agent_retry_exceeded"
        exception = Exception("Test exception")
        self.failure_manager.agent_failure_counts[agent_name] = 3

        # This should now default to CONTINUE behavior as retries are exceeded
        self.failure_manager.handle_failure(
            agent_name, exception, RecoveryStrategy.RETRY, max_retries=3
        )
        self.assertEqual(self.failure_manager.agent_failure_counts[agent_name], 4)
        self.rollback_manager.rollback.assert_called_with(agent_name)


    def test_handle_failure_halt_strategy(self):
        agent_name = "test_agent_halt"
        exception = Exception("Critical error")

        with self.assertRaises(Exception) as context:
            self.failure_manager.handle_failure(
                agent_name, exception, RecoveryStrategy.HALT
            )

        self.assertTrue("Critical error" in str(context.exception))
        self.assertEqual(self.failure_manager.agent_failure_counts[agent_name], 1)
        self.rollback_manager.rollback.assert_not_called()

if __name__ == '__main__':
    unittest.main()