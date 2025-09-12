"""
A demonstration script to showcase the QuantumAgentBrain in action.
This script initializes a mock environment and runs the brain's full pipeline
to generate a structured Intent and Plan.
"""
import uuid
import asyncio
import json
from typing import Dict, Any, List, Optional, Type

from pydantic import BaseModel

from agent.brain import QuantumAgentBrain, QuantumAgent, CapabilityManager
from core.types import Intent, Plan, QCState
from llm.client import LLMClient

# --- Mock LLM Client for Demonstration ---

class MockLLMClient(LLMClient):
    """
    A mock LLM client that returns pre-defined structured responses based on the prompt.
    This allows testing the brain's logic without live API calls.
    """
    def __init__(self, api_key: str = "mock_key", model: str = "mock_model"):
        super().__init__(api_key, model)

    async def _do_chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict:
        """
        Simulates the LLM call. It checks the content of the user prompt
        to decide which canned response to return.
        """
        print("\n--- MockLLMClient: Simulating LLM Call ---")
        user_prompt = messages[-1]['content']

        if "intent_parsing" in messages[0]['content']:
            print("--- MockLLMClient: Detected Intent Parsing task. Returning canned Intent JSON. ---")
            response_content = {
              "goal": "Develop a new, secure, public-facing API for processing payments, which must include a rate-limiting mechanism.",
              "cnl_translation": "A secure payment API shall be created. The API must enforce rate limiting on incoming requests.",
              "constraints": {
                "security_level": "PCI-DSS_Compliant",
                "feature": "rate_limiting",
                "max_requests_per_minute": 100,
                "authentication": "OAuth2"
              },
              "priority": "CRITICAL",
              "acceptance_criteria": [
                "API endpoints for creating charge, retrieving transaction, and refunding are implemented.",
                "All API endpoints are protected by OAuth2 authentication.",
                "Rate limiting is enforced at 100 requests/minute per user.",
                "The API passes a third-party security audit and PCI-DSS compliance scan."
              ],
              "energy_estimate": {
                "e_complexity": 8.0,
                "e_coupling": 7.5,
                "e_constraint": 9.0,
                "e_debt": 1.0,
                "total_estimated_energy": 25.5
              },
              "risk_assessment": {
                "bound_type": "chernoff",
                "confidence_level": 0.99,
                "failure_probability": 0.01,
                "details": "High risk due to handling of financial data and external security requirements."
              },
              "requires_approval": True,
              "estimated_effort": "HIGH"
            }
        elif "planning" in messages[0]['content']:
            print("--- MockLLMClient: Detected Planning task. Returning canned Plan JSON. ---")
            intent_json_str = user_prompt.split('Generate a complete plan for the following intent:\n')[-1]
            intent_dict = json.loads(intent_json_str)
            response_content = {
              "id": f"plan-{uuid.uuid4()}",
              "intent": intent_dict,
              "nodes": [
                {"id": "setup-project", "description": "Initialize project structure, dependencies, and CI/CD.", "agent_name": "SchrodingerDev", "tool_call": "create_project()", "preconditions": ["Intent approved"], "postconditions": ["Project exists"], "energy_barrier": 3.0},
                {"id": "define-schema", "description": "Define OpenAPI schema for payment endpoints.", "agent_name": "PlanckForge", "tool_call": "design_schema()", "preconditions": ["Project exists"], "postconditions": ["api_schema.yaml is valid"], "energy_barrier": 5.0},
                {"id": "implement-auth", "description": "Implement OAuth2 middleware.", "agent_name": "PauliGuard", "tool_call": "implement_oauth()", "preconditions": ["api_schema.yaml is valid"], "postconditions": ["Endpoints protected"], "energy_barrier": 8.0},
                {"id": "implement-ratelimit", "description": "Implement token bucket rate limiter.", "agent_name": "PauliGuard", "tool_call": "implement_ratelimiter()", "preconditions": ["Endpoints protected"], "postconditions": ["Rate limit functional"], "energy_barrier": 6.0},
                {"id": "implement-payment-logic", "description": "Implement core payment charge/refund logic.", "agent_name": "SchrodingerDev", "tool_call": "implement_payment_core()", "preconditions": ["api_schema.yaml is valid"], "postconditions": ["Payments can be processed"], "energy_barrier": 10.0},
                {"id": "deploy-staging", "description": "Deploy to staging environment.", "agent_name": "SchrodingerDev", "tool_call": "deploy(env='staging')", "preconditions": ["All implementation tasks complete"], "postconditions": ["App is live on staging"], "energy_barrier": 4.0}
              ],
              "edges": [
                {"from_node": "setup-project", "to_node": "define-schema", "transition_probability": 1.0, "condition": "Success"},
                {"from_node": "define-schema", "to_node": "implement-auth", "transition_probability": 1.0, "condition": "Success"},
                {"from_node": "implement-auth", "to_node": "implement-ratelimit", "transition_probability": 1.0, "condition": "Success"},
                {"from_node": "define-schema", "to_node": "implement-payment-logic", "transition_probability": 1.0, "condition": "Success"},
                {"from_node": "implement-ratelimit", "to_node": "deploy-staging", "transition_probability": 1.0, "condition": "Success"},
                {"from_node": "implement-payment-logic", "to_node": "deploy-staging", "transition_probability": 1.0, "condition": "Success"}
              ],
              "metadata": {"required_capabilities": ["READ_FILES", "WRITE_FILES", "EXECUTE_TOOLS"], "estimated_time_seconds": 7200, "risk_assessment": intent_dict['risk_assessment']},
              "verification_points": [{"node_id": "deploy-staging", "proof_obligation": "Prove that p99 latency < 500ms and all security checks pass."}],
              "energy_impact": {"initial_energy": intent_dict['context']['system_state']['energy'], "predicted_final_energy": intent_dict['context']['system_state']['energy'] + 36.0, "delta_e": 36.0},
              "convergence_proof": {"theorem": "Banach Fixed-Point Theorem", "proof_sketch": "The plan is an acyclic graph of tasks, guaranteeing termination.", "is_verified": False},
              "lyapunov_certificate": {"function_definition": "V(x) = sum of energy_barriers of remaining tasks.", "descent_guarantee": "Each step reduces V(x).", "is_verified": False}
            }
        else:
            response_content = {"error": "Mock client did not understand the prompt."}

        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "model": self.model,
            "choices": [{"message": {"role": "assistant", "content": json.dumps(response_content)}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 500, "completion_tokens": 500, "total_tokens": 1000}
        }

# --- Main Demonstration ---

async def main():
    """
    Runs the full demonstration of the QuantumAgentBrain.
    """
    print("--- Setting up the QuantaCirc Demonstration Environment ---")

    llm_client = MockLLMClient()
    capability_manager = CapabilityManager()

    agents = {
        "PlanckForge": QuantumAgent("PlanckForge"),
        "SchrodingerDev": QuantumAgent("SchrodingerDev"),
        "PauliGuard": QuantumAgent("PauliGuard"),
    }

    brain = QuantumAgentBrain(
        llm_client=llm_client,
        agents=agents,
        capability_manager=capability_manager,
    )

    print("\n--- Starting Demonstration Pipeline ---")

    user_request = "Build a secure payment API with rate limiting"
    session_context = {"session_id": uuid.uuid4()}

    # 1. Extract the structured Intent
    intent = await brain.extract_intent(user_request, session_context=session_context)
    print("\n--- (1) DELIVERABLE: Structured Intent ---")
    print(intent.model_dump_json(indent=2))

    # 2. Generate the executable Plan
    plan = await brain.generate_plan(intent)
    print("\n--- (2) DELIVERABLE: Executable Plan ---")
    print(plan.model_dump_json(indent=2))

    # 3. Retrieve memories (placeholder)
    brain.retrieve_memories(intent)

    # 4. Evolve system state after plan 'execution'
    final_state = brain.evolve_state(plan)
    print("\n--- (3) Final System State (QCState) ---")
    print(final_state.model_dump_json(indent=2))

    # 5. Store successful pattern (placeholder)
    brain.store_successful_pattern(plan, {"status": "success"})

    print("\n--- Demonstration Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
