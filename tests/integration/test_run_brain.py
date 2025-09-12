import unittest
import asyncio
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock

# Ensure the script can find the root modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from run_brain import main as run_brain_main

class TestRunBrainIntegration(unittest.TestCase):

    def _get_canned_response(self, prompt_content):
        """
        Returns a canned response based on whether it's an intent or planning prompt.
        This simulates the behavior of the LLM for testing purposes.
        """
        if "intent_parsing" in prompt_content:
            return {
              "goal": "Mocked: Develop a secure payment API.",
              "cnl_translation": "Mocked: A secure API for payments shall be created.",
              "constraints": {"security": "high"},
              "priority": "CRITICAL",
              "acceptance_criteria": ["PCI compliant"],
              "energy_estimate": {"e_complexity": 10.0, "e_coupling": 8.0, "e_constraint": 12.0, "e_debt": 2.0, "total_estimated_energy": 32.0},
              "risk_assessment": {"bound_type": "chernoff", "confidence_level": 0.99, "failure_probability": 0.01, "details": "High risk"},
              "requires_approval": True,
              "estimated_effort": "HIGH"
            }
        elif "planning" in prompt_content:
            # A simplified plan for testing purposes
            return {
              "id": "mock-plan-123",
              "intent": json.loads(prompt_content.split('Generate a complete plan for the following intent:\n')[-1]),
              "nodes": [{"id": "node-1", "description": "Mocked node", "agent_name": "PlanckForge", "tool_call": "mock_tool()", "preconditions": [], "postconditions": [], "energy_barrier": 1.0}],
              "edges": [],
              "metadata": {"required_capabilities": ["READ_FILES"], "estimated_time_seconds": 3600, "risk_assessment": {"bound_type": "chernoff", "confidence_level": 0.99, "failure_probability": 0.01, "details": "High risk"}},
              "verification_points": [],
              "energy_impact": {"initial_energy": 0, "predicted_final_energy": 10, "delta_e": 10},
              "convergence_proof": {"theorem": "Mock Proof", "proof_sketch": "Mock sketch", "is_verified": False},
              "lyapunov_certificate": {"function_definition": "V(x)=0", "descent_guarantee": "Mock guarantee", "is_verified": False}
            }
        return {"error": "Unknown prompt type"}

    @patch('llm.client.OpenAIClient._do_chat')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_run_brain_end_to_end(self, mock_do_chat):
        """
        Tests that the run_brain.py script executes end-to-end without errors,
        using a mocked LLM client.
        """
        # Configure the async mock to behave like the real method
        async def chat_side_effect(*args, **kwargs):
            # args[0] will be `self`, args[1] will be `messages`
            messages = args[1]
            canned_response = self._get_canned_response(messages[0]['content'])
            return {
                "id": "mock-completion-id",
                "model": "mock-model",
                "choices": [{"message": {"role": "assistant", "content": json.dumps(canned_response)}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 100, "total_tokens": 200}
            }

        mock_do_chat.side_effect = chat_side_effect

        # Run the main function from the script
        # We need to run the asyncio event loop
        try:
            asyncio.run(run_brain_main())
            # If it runs without exceptions, the test is largely successful.
            # For more robustness, we could capture stdout and check its content.
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"run_brain.py failed with an exception: {e}")

if __name__ == '__main__':
    unittest.main()
