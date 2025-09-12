import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import uuid

from agent.brain import QuantumAgentBrain
from core.schemas import Intent, Plan, EnergyEstimate, RiskBound, QuantumSignatures, IntentContext
from llm.capability_tokens import CapabilityManager

# Mock the LLMClient and QuantumAgent to isolate the brain for testing
class MockLLMClient:
    def generate(self, prompt: str):
        return "mocked response"

class MockQuantumAgent:
    def __init__(self, name):
        self.name = name

class TestQuantumAgentBrain(unittest.TestCase):

    def setUp(self):
        """Set up a QuantumAgentBrain instance before each test."""
        self.mock_llm_client = MockLLMClient()
        self.mock_agents = {"test_agent": MockQuantumAgent("test_agent")}
        self.mock_capability_manager = CapabilityManager()
        self.brain = QuantumAgentBrain(
            llm_client=self.mock_llm_client,
            agents=self.mock_agents,
            capability_manager=self.mock_capability_manager,
            system_dimensionality=2
        )

    def test_initialization(self):
        """Test that the brain initializes correctly."""
        self.assertIsInstance(self.brain, QuantumAgentBrain)
        self.assertEqual(self.brain.dimensionality, 2)
        self.assertIsNotNone(self.brain.hamiltonian)
        self.assertIsNotNone(self.brain.psi_current)
        self.assertEqual(self.brain.hamiltonian.shape, (2, 2))
        self.assertEqual(self.brain.psi_current.shape, (2,))
        self.assertAlmostEqual(np.linalg.norm(self.brain.psi_current), 1.0)

    def test_extract_intent_returns_detailed_intent(self):
        """Test that extract_intent returns a detailed Intent object."""
        user_input = "Create a detailed test"
        session_id = str(uuid.uuid4())
        intent = self.brain.extract_intent(user_input, session_id)

        self.assertIsInstance(intent, Intent)
        self.assertEqual(intent.goal, user_input)
        self.assertIsInstance(intent.energy_estimate, EnergyEstimate)
        self.assertIsInstance(intent.risk_assessment, RiskBound)
        self.assertIsInstance(intent.quantum_signatures, QuantumSignatures)
        self.assertIsInstance(intent.context, IntentContext)
        self.assertEqual(intent.context.session_id, session_id)

    def test_generate_plan_returns_detailed_plan(self):
        """Test that generate_plan returns a detailed Plan object."""
        # First, create a valid Intent object to pass to the method
        intent = self.brain.extract_intent("A test intent", "session-for-plan")

        plan = self.brain.generate_plan(intent)

        self.assertIsInstance(plan, Plan)
        self.assertEqual(plan.intent, intent)
        self.assertIsNotNone(plan.id)
        self.assertIsInstance(plan.nodes, list)
        self.assertIsInstance(plan.edges, list)
        self.assertIsNotNone(plan.lyapunov_certificate)
        self.assertTrue(plan.lyapunov_certificate.descent_guarantee)

    def test_evolve_state(self):
        """Test the quantum state evolution."""
        initial_psi = self.brain.psi_current.copy()

        dt = 0.1
        new_psi = self.brain.evolve_state(dt)

        self.assertFalse(np.allclose(initial_psi, new_psi))
        self.assertAlmostEqual(np.linalg.norm(new_psi), 1.0, places=5)
        self.assertTrue(np.allclose(self.brain.psi_current, new_psi))

    def test_hamiltonian_is_hermitian(self):
        """Test that the generated Hamiltonian is Hermitian."""
        H = self.brain.hamiltonian
        self.assertTrue(np.allclose(H, H.conj().T))

if __name__ == '__main__':
    unittest.main()
