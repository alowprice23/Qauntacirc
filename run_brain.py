"""
A demonstration script to showcase the QuantumAgentBrain in action.
This script initializes a mock environment and runs the brain's full pipeline
to generate a structured Intent and Plan.
"""
import uuid
import asyncio
import json
import os
from typing import Dict, Any, List, Optional, Type

from pydantic import BaseModel

from agent.brain import QuantumAgentBrain, QuantumAgent, CapabilityManager
from core.data_models import Intent, Plan, QCState
from llm.client import LLMClient, OpenAIClient

# This is a placeholder for a more sophisticated agent management system.
# In a real application, these would be loaded dynamically.
AGENTS = {
    "PlanckForge": QuantumAgent(name="PlanckForge"),
    "SchrodingerDev": QuantumAgent(name="SchrodingerDev"),
    "PauliGuard": QuantumAgent(name="PauliGuard"),
    "UncertainAI": QuantumAgent(name="UncertainAI"),
    "TunnelFix": QuantumAgent(name="TunnelFix"),
    "BoseBoost": QuantumAgent(name="BoseBoost"),
    "PhononFlow": QuantumAgent(name="PhononFlow"),
    "FluctuaTest": QuantumAgent(name="FluctuaTest"),
    "HydroSpread": QuantumAgent(name="HydroSpread"),
    "LondonLink": QuantumAgent(name="LondonLink"),
}


async def main():
    """
    Main execution function to run the QuantumAgentBrain.
    """
    print("Starting QuantaCirc Agent Brain...")

    # 1. Configuration and Initialization
    # Ensure the OpenAI API key is set in the environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    # Initialize the components
    llm_client = OpenAIClient(api_key=api_key, model="gpt-4-turbo-preview")
    capability_manager = CapabilityManager()

    # The brain is the central orchestrator
    brain = QuantumAgentBrain(
        llm_client=llm_client,
        agents=AGENTS,
        capability_manager=capability_manager,
    )

    # 2. Define the User's Goal
    # This is the deliverable specified in the problem description
    user_goal = "Build a secure payment API with rate limiting"
    session_context = {"session_id": uuid.uuid4()}

    try:
        # 3. Execute the Brain's Processing Pipeline
        # Step 3a: Extract a structured Intent from the user's goal
        intent = await brain.extract_intent(user_goal, session_context)
        print("\n--- Extracted Intent ---")
        print(intent.model_dump_json(indent=2))

        # Step 3b: Retrieve relevant memories (currently a placeholder)
        memories = brain.retrieve_memories(intent)

        # Step 3c: Generate an executable Plan from the Intent
        plan = await brain.generate_plan(intent, memories)
        print("\n--- Generated Plan ---")
        print(plan.model_dump_json(indent=2))

        # Step 3d: Evolve the system state after the plan is (notionally) executed
        final_state = brain.evolve_state(plan)
        print("\n--- Final System State ---")
        print(final_state.model_dump_json(indent=2))

        # Step 3e: Store the successful pattern (currently a placeholder)
        brain.store_successful_pattern(plan, {"status": "success"})


    except Exception as e:
        print(f"\nAn error occurred during brain execution: {e}")
        import traceback
        traceback.print_exc()

    print("\nQuantaCirc Agent Brain run complete.")


if __name__ == "__main__":
    # To run this, you need to have your OPENAI_API_KEY set as an environment variable.
    # Example:
    # export OPENAI_API_KEY='your_key_here'
    # python run_brain.py
    asyncio.run(main())
