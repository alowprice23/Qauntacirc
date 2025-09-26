import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from core.orchestrator import Orchestrator
from core.system_state import SystemState
from agents.base.agent import QuantumAgent

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.config = {}
        self.nats_client = MagicMock()
        self.nats_client.publish = AsyncMock()
        self.nats_client.subscribe = AsyncMock()

        # Mock the StateManager's get_current_state to avoid real NATS calls
        self.orchestrator = Orchestrator(self.config, self.nats_client)
        self.orchestrator.state_manager.get_current_state = AsyncMock(side_effect=lambda s: asyncio.FromResult(s))


    def test_register_agent(self):
        agent = QuantumAgent(name="test_agent")
        dependencies = {"inputs": [], "outputs": ["test_output"]}
        self.orchestrator.register_agent(agent, dependencies)

        self.assertIn("test_agent", self.orchestrator.agents)
        self.assertEqual(self.orchestrator.agents["test_agent"], agent)
        self.assertIn("test_agent", self.orchestrator.dependency_graph.graph)

    def test_dependency_resolution(self):
        agent_a = QuantumAgent(name="agent_a")
        agent_b = QuantumAgent(name="agent_b")

        self.orchestrator.register_agent(agent_a, {"outputs": ["output_a"]})
        self.orchestrator.register_agent(agent_b, {"inputs": ["output_a"], "outputs": ["output_b"]})

        execution_plan = self.orchestrator.dependency_graph.resolve_dependencies()
        self.assertEqual(execution_plan, ["agent_a", "agent_b"])

    def test_run_orchestrator(self):
        # Mock agents
        agent_a = QuantumAgent(name="agent_a")
        agent_a.execute = MagicMock(return_value={"data_a": "value_a"})

        agent_b = QuantumAgent(name="agent_b")
        agent_b.execute = MagicMock(return_value={"data_b": "value_b"})

        self.orchestrator.register_agent(agent_a, {"outputs": ["output_a"]})
        self.orchestrator.register_agent(agent_b, {"inputs": ["output_a"]})

        initial_state = SystemState()
        task = "test_task"

        final_state = self.loop.run_until_complete(
            self.orchestrator.run(initial_state, task)
        )

        # Check that agents were called in the correct order
        agent_a.execute.assert_called_once()
        agent_b.execute.assert_called_once()

        # Check final state
        self.assertIn("data_a", final_state.data)
        self.assertEqual(final_state.data["data_a"], "value_a")
        self.assertIn("data_b", final_state.data)
        self.assertEqual(final_state.data["data_b"], "value_b")

    def test_failure_handling(self):
        agent_a = QuantumAgent(name="agent_a")
        agent_a.execute = MagicMock(side_effect=Exception("Agent A failed"))

        self.orchestrator.register_agent(agent_a, {})

        initial_state = SystemState(data={"initial": "data"})
        task = "test_task"

        final_state = self.loop.run_until_complete(
            self.orchestrator.run(initial_state, task, simulate_failure="agent_a")
        )

        # Since the default recovery is 'continue', the state should be rolled back
        # to the one before the failing agent.
        self.assertEqual(final_state.data, {"initial": "data"})

    def tearDown(self):
        self.loop.close()

if __name__ == '__main__':
    unittest.main()