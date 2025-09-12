"""
A demonstration script to showcase the QuantumAgentBrain in action.
This script initializes a mock environment, integrates a live agent,
and runs the brain's full pipeline.
"""
import uuid
import asyncio
from typing import Dict, Any, List, Optional

import numpy as np

from agent.brain import QuantumAgentBrain
from agents.base.agent import QuantumAgent
from agents.planck_forge.agent import PlanckForgeAgent
from core.types import AgentTask, AgentResult, QCState, Status, SoftwareState, EnergyComponents
from core.schemas import Plan
from llm.client import LLMClient
from llm.capability_tokens import CapabilityManager

# --- Mock Implementations for Demonstration ---

class MockLLMClient(LLMClient):
    """A mock LLM client that returns pre-defined responses."""
    def __init__(self, api_key: str = "mock_key", model: str = "mock_model"):
        super().__init__(api_key, model)

    def complete(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Simulates the LLM call. This is now a synchronous method to match the base class.
        The response is now a JSON object with a 'tasks' key, as expected by the parser.
        """
        print("\n--- MockLLMClient: Completing chat ---")
        simulated_response_content = """
        {
          "tasks": [
            {
              "id": "API-001",
              "description": "Define the API endpoints and data models for the payment service.",
              "dependencies": [],
              "verification_criteria": ["OpenAPI specification is created.", "Pydantic models for request/response are defined."]
            },
            {
              "id": "API-002",
              "description": "Implement the core payment processing logic.",
              "dependencies": ["API-001"],
              "verification_criteria": ["Payment function can process successful payments.", "Payment function handles failed payments gracefully."]
            }
          ]
        }
        """
        return {"response": simulated_response_content}

    def _do_generate(self, prompt: str, **kwargs) -> str:
        return "Simulated LLM response."

    def _do_chat(self, messages: List[Dict[str, str]], **kwargs):
        pass

    def embed(self, texts: List[str], **kwargs) -> List[List[float]]:
        return [[np.random.rand() for _ in range(10)] for _ in texts]

# Mock dependencies for the live agent
class MockStateSpace:
    def get_current_state(self): pass
class MockEnergyCalculator:
    def compute_static_energy(self, metrics): return sum(metrics.values())
class MockMetricsLogger:
    def register_counter(self, name, description): pass
    def register_histogram(self, name, description): pass
    def increment_counter(self, name): pass
    def log_duration(self, name): return self
    def __enter__(self): pass
    def __exit__(self, type, value, traceback): pass
class MockPolicyEngine:
    def validate(self, proposal): return True
class MockAgentMemory:
    def record_decision(self, state, proposal, action): pass

# --- Main Demonstration ---

async def main():
    """
    Runs the full demonstration of the QuantumAgentBrain.
    """
    print("--- Setting up the QuantaCirc Demonstration Environment ---")

    llm_client = MockLLMClient()
    capability_manager = CapabilityManager()

    mock_state_space = MockStateSpace()
    mock_energy_calculator = MockEnergyCalculator()
    mock_metrics_logger = MockMetricsLogger()
    mock_policy_engine = MockPolicyEngine()
    mock_agent_memory = MockAgentMemory()

    planck_forge_agent = PlanckForgeAgent(
        state_space=mock_state_space,
        energy_calculator=mock_energy_calculator,
        metrics_logger=mock_metrics_logger,
        policy_engine=mock_policy_engine,
        agent_memory=mock_agent_memory,
        llm_client=llm_client
    )

    agents = {
        "PlanckForge": planck_forge_agent,
        "SchrodingerDev": MockQuantumAgent("SchrodingerDev"),
        "PauliGuard": MockQuantumAgent("PauliGuard"),
    }

    brain = QuantumAgentBrain(
        llm_client=llm_client,
        agents=agents,
        capability_manager=capability_manager,
        system_dimensionality=4
    )

    print("\n--- Starting Demonstration Pipeline ---")

    user_request = "Build a secure payment API with rate limiting"

    intent = brain.extract_intent(user_request, session_id="session-123")
    print("\n--- Extracted Intent (Detailed Schema) ---")
    print(intent.model_dump_json(indent=2))

    plan = brain.generate_plan(intent)
    print("\n--- Generated Plan (Detailed Schema) ---")
    print(plan.model_dump_json(indent=2))

    print("\n--- Dispatching Task to Live PlanckForgeAgent ---")

    planck_forge_task_node = next((node for node in plan.nodes if node.agent_name == "PlanckForge"), None)

    if planck_forge_task_node:
        initial_software_state = SoftwareState(component_versions={}, config_hashes={})
        initial_energy_components = EnergyComponents(static=100.0, dynamic=50.0, interaction=20.0)
        initial_state = QCState(
            software_state=initial_software_state,
            energy=initial_energy_components.total,
            energy_components=initial_energy_components,
            lyapunov_potential=180.0,
            contraction_factor=1.0,
            metadata={"requirement_text": user_request}
        )

        proposal = await planck_forge_agent.analyze_state(initial_state)

        if planck_forge_agent.validate_proposal(proposal):
            action_result = planck_forge_agent.execute(proposal)
            print("\n--- Result from PlanckForgeAgent ---")
            print(action_result.model_dump_json(indent=2))
        else:
            print("\n--- PlanckForgeAgent proposal was invalid ---")
            print(f"Reason: {proposal.reason}")
    else:
        print("\n--- No task found for PlanckForgeAgent in the generated plan ---")

    initial_psi = brain.psi_current
    print(f"\n--- Initial Quantum State (psi_current) ---\n{initial_psi}")
    final_psi = brain.evolve_state(dt=0.1)
    print(f"New Quantum State:\n{final_psi}")

    print("\n--- Demonstration Complete ---")

class MockQuantumAgent(QuantumAgent):
    """A mock quantum agent for demonstration purposes."""
    def __init__(self, name: str):
        self.name = name
        self.agent_id = str(uuid.uuid4())
    def analyze_state(self, state: QCState) -> AgentTask: pass
    def validate_proposal(self, proposal: AgentTask) -> bool: return True
    def execute(self, proposal: AgentTask) -> AgentResult: pass

if __name__ == "__main__":
    asyncio.run(main())
