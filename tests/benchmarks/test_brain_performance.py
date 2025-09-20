import pytest
import asyncio
import uuid
import json
from typing import Dict, Any, List, Optional

from pydantic import BaseModel

# --- Imports from the application ---
from agent.brain import QuantumAgentBrain, QuantumAgent, CapabilityManager
from llm.client import LLMClient
from core.types import Intent, Plan, QCState

# --- Mock LLM Client (copied and simplified for benchmarks) ---
class MockLLMClient(LLMClient):
    """
    A mock LLM client that returns minimal valid structured responses.
    """
    def __init__(self, api_key: str = "mock_key", model: str = "mock_model"):
        super().__init__(api_key, model)
        # Minimal valid response for an Intent
        self.intent_response = {
            "goal": "Build a secure payment API with rate limiting",
            "cnl_translation": "A secure payment API shall be built, and it will have rate limiting.",
            "constraints": {}, "priority": "LOW",
            "acceptance_criteria": [], "energy_estimate": {"e_complexity": 1,"e_coupling": 1,"e_constraint": 1,"e_debt": 1,"total_estimated_energy": 4},
            "risk_assessment": {"bound_type": "chernoff", "confidence_level": 1, "failure_probability": 0, "details": ""},
            "requires_approval": False, "estimated_effort": "TRIVIAL"
        }
        # Minimal valid response for a PlanGenerationResult
        self.plan_generation_response = {
            "nodes": [], "edges": [],
            "metadata": {"required_capabilities": [], "estimated_time_seconds": 0, "risk_assessment": self.intent_response['risk_assessment']},
            "verification_points": []
        }

    async def _do_chat(self, messages: List[Dict[str, str]], quantum_context: Optional[QCState] = None, **kwargs) -> Dict:
        system_prompt = messages[0]['content']
        user_prompt = messages[-1]['content']

        # Check for a unique field from the PlanGenerationResult schema
        if '"verification_points"' in system_prompt:
            response_content = self.plan_generation_response
        elif '"cnl_translation"' in system_prompt:
            response_content = self.intent_response
        else:
            response_content = {"error": "Mock client did not understand the prompt."}

        return {
            "id": f"chatcmpl-{uuid.uuid4()}", "model": self.model,
            "choices": [{"message": {"role": "assistant", "content": json.dumps(response_content)}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}
        }

# --- Benchmark Setup ---
# This is required to run async functions in pytest benchmarks
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def brain_instance():
    """Sets up the QuantumAgentBrain with a mock client for benchmarking."""
    llm_client = MockLLMClient()
    capability_manager = CapabilityManager()
    agents = {"default": QuantumAgent("default")}
    brain = QuantumAgentBrain(
        llm_client=llm_client,
        agents=agents,
        capability_manager=capability_manager,
    )
    return brain

# --- Benchmark Tests ---

def test_benchmark_extract_intent(benchmark, brain_instance, event_loop):
    """Benchmark the performance of the extract_intent method."""
    user_request = "Build a secure payment API with rate limiting"
    session_context = {"session_id": uuid.uuid4()}

    def f():
        return event_loop.run_until_complete(brain_instance.extract_intent(user_request, session_context))

    benchmark(f)

def test_benchmark_generate_plan(benchmark, brain_instance, event_loop):
    """Benchmark the performance of the generate_plan method."""
    # First, generate an intent to use as input. This part is not benchmarked.
    user_request = "Build a secure payment API with rate limiting"
    session_context = {"session_id": uuid.uuid4()}
    intent = event_loop.run_until_complete(brain_instance.extract_intent(user_request, session_context))

    def f():
        return event_loop.run_until_complete(brain_instance.generate_plan(intent))

    benchmark(f)
