# agents/phonon_flow/agent.py
"""
PhononFlow Agent: Optimizes data flow and communication patterns.

This agent analyzes the interactions between system components and proposes
architectural changes to improve data flow efficiency, such as introducing
caches, message queues, or asynchronous processing.
"""
import asyncio
import re
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

class PhononFlowAgent(QuantumAgent):
    """
    The PhononFlow Agent is a distributed systems architect.

    It looks at the macro-level communication patterns and suggests
    refactorings to improve the overall efficiency and scalability of the system,
    targeting the interaction energy component.
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
            name="phonon_flow",
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
        Analyzes the system's communication patterns and proposes optimizations.

        Args:
            state: The current state, containing a map of all source code files.

        Returns:
            A proposal containing a data flow optimization plan.
        """
        all_source_files = state.get("source_code_map", {})
        if not all_source_files:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.SUCCESS, reason="No source code to analyze.")

        # 1. Analyze data flow to find a pattern (simulated)
        data_flow_description = ops.analyze_data_flow(all_source_files)

        if "No clear" in data_flow_description:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.SUCCESS, reason="No optimizable data flow pattern found.")

        # 2. Generate an optimization plan using the LLM
        prompt_spec = prompts.get_prompt("optimize_data_flow")
        formatted_prompt = prompt_spec.format(data_flow_description=data_flow_description)

        llm_response = await self.llm_client.complete({"prompt": formatted_prompt})

        try:
            plan = ops.parse_optimization_plan(llm_response["content"])
            return Proposal(
                agent_id=self.agent_id,
                data={"optimization_plan": plan},
                status=Status.SUCCESS
            )
        except ops.DataFlowError as e:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.FAILED, reason=f"Failed to generate optimization plan: {e}")

    def validate_proposal(self, proposal: Proposal) -> bool:
        """
        Validates the optimization plan.

        For now, we just check the structure of the plan. A real system might
        have formal models to verify the proposed architecture.
        """
        if proposal.status != Status.SUCCESS:
            return False

        if "optimization_plan" not in proposal.data:
            return True # An empty proposal is a valid one (no-op)

        try:
            ops.parse_optimization_plan(json.dumps(proposal.data["optimization_plan"]))
            return True
        except ops.DataFlowError as e:
            print(f"Data flow optimization plan validation failed: {e}")
            return False

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the proposal by calculating the interaction energy reduction.
        """
        if "optimization_plan" not in proposal.data:
            return Action(agent_id=self.agent_id, data={}, status=Status.SUCCESS)

        plan = proposal.data["optimization_plan"]

        # 1. Calculate the reduction in interaction energy.
        # This is a heuristic based on the LLM's stated expected outcome.
        # E.g., "Reduces API response time by 50%"
        outcome_text = plan.get("expected_outcome", "")

        # Simple regex to extract a percentage improvement
        match = re.search(r'(\d+)%', outcome_text)
        if match:
            percent_improvement = float(match.group(1))
        else:
            percent_improvement = 0.0

        # The reduction in interaction energy is proportional to the improvement.
        # The weight `w_data_flow_efficiency` would be defined in the calculator's config.
        energy_reduction = self.energy_calculator.config.get("w_data_flow_efficiency", 1.0) * percent_improvement

        # 2. Create the action
        action_data = {
            "optimization_plan": plan,
            "energy_impact": {
                "interaction": -energy_reduction
            }
        }

        return Action(
            agent_id=self.agent_id,
            data=action_data,
            status=Status.SUCCESS
        )
