# agents/fluctua_test/agent.py
"""
FluctuaTest Agent: Runs chaos tests to ensure system stability under stress.

This agent designs and executes chaos engineering experiments to proactively
find weaknesses in a system's resilience.
"""
import asyncio
import json
from typing import Dict, Any, Optional, List

from agents.base.agent import QuantumAgent
from core.state_space import StateSpace
from core.energy_calculator import EnergyCalculator
from core.types import Proposal, State, Action, Status
from monitoring.metrics import MetricsLogger
from agents.base.policies import PolicyEngine
from agents.base.memory import AgentMemory
from llm.client import LLMClient

from . import prompts
from . import ops

class FluctuaTestAgent(QuantumAgent):
    """
    The FluctuaTest Agent is a chaos engineer.

    It designs experiments to inject faults into the system and observes the
    impact, verifying that the system degrades gracefully rather than failing
    catastrophically. A successful experiment increases confidence in the

    system's resilience, thus lowering its dynamic energy.
    """
    def __init__(
        self,
        state_space: StateSpace,
        energy_calculator: EnergyCalculator,
        metrics_logger: MetricsLogger,
        policy_engine: PolicyEngine,
        agent_memory: AgentMemory,
        llm_client: LLMClient,
        agent_id: Optional[str] = None,
    ):
        super().__init__(
            name="fluctua_test",
            state_space=state_space,
            energy_calculator=energy_calculator,
            metrics_logger=metrics_logger,
            policy_engine=policy_engine,
            agent_memory=agent_memory,
            agent_id=agent_id,
        )
        self.llm_client = llm_client

    async def analyze_state(self, state: State) -> Proposal:
        """
        Analyzes the system architecture and proposes a chaos experiment.

        Args:
            state: The current state, containing a map of all source code files.

        Returns:
            A proposal containing a chaos engineering experiment plan.
        """
        all_source_files = state.get("source_code_map", {})
        if not all_source_files:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.SUCCESS, reason="No source code to analyze.")

        # 1. Get a description of the system architecture (simulated)
        architecture_description = ops.extract_architecture(all_source_files)

        # 2. Generate a chaos test plan using the LLM
        prompt_spec = prompts.get_prompt("generate_chaos_test")
        formatted_prompt = prompt_spec.format(architecture_description=architecture_description)

        llm_response = await self.llm_client.complete({"prompt": formatted_prompt})

        try:
            plan = ops.parse_chaos_experiment_plan(llm_response["content"])
            return Proposal(
                agent_id=self.agent_id,
                data={"chaos_experiment_plan": plan},
                status=Status.SUCCESS
            )
        except ops.ChaosTestError as e:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.FAILED, reason=f"Failed to generate chaos test plan: {e}")

    def validate_proposal(self, proposal: Proposal) -> bool:
        """Validates the chaos experiment plan."""
        if proposal.status != Status.SUCCESS:
            return False

        if "chaos_experiment_plan" not in proposal.data:
            return True # An empty proposal is a valid one

        try:
            ops.parse_chaos_experiment_plan(json.dumps(proposal.data["chaos_experiment_plan"]))
            return True
        except ops.ChaosTestError as e:
            print(f"Chaos experiment plan validation failed: {e}")
            return False

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the chaos experiment and calculates the energy impact.
        """
        if "chaos_experiment_plan" not in proposal.data:
            return Action(agent_id=self.agent_id, data={}, status=Status.SUCCESS)

        plan = proposal.data["chaos_experiment_plan"]

        # 1. Run the fault injection (simulated)
        injection_result = ops.inject_fault(plan["fault_to_inject"])

        # 2. Determine the outcome and calculate energy impact.
        # For this simulation, we'll assume the experiment is always successful
        # and confirms the system's resilience.
        experiment_succeeded = injection_result["status"] == "SUCCESS"

        energy_reduction = 0
        if experiment_succeeded:
            # A successful test reduces uncertainty about resilience.
            # We model this as a reduction in dynamic energy.
            resilience_confirmed_value = 1.0
            energy_reduction = self.energy_calculator.config.get("w_resilience", 10.0) * resilience_confirmed_value

        # 3. Create the action
        action_data = {
            "chaos_experiment_plan": plan,
            "experiment_result": injection_result,
            "energy_impact": {
                "dynamic": -energy_reduction
            }
        }

        return Action(
            agent_id=self.agent_id,
            data=action_data,
            status=Status.SUCCESS
        )
