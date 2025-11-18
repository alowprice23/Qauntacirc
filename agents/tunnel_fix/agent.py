# agents/tunnel_fix/agent.py
"""
TunnelFix Agent: Automatically proposes and validates fixes for bugs.

This agent uses static analysis and LLM-based reasoning to generate patches
for code that is failing its test cases. It aims to reduce dynamic energy
by eliminating errors.
"""
import asyncio
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

class TunnelFixAgent(QuantumAgent):
    """
    The TunnelFix Agent is a bug-fixing specialist.

    It takes a failing test case as input, analyzes the associated code,
    and generates a patch to resolve the issue. Its validation process
    involves ensuring the proposed patch makes the test pass.
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
            name="tunnel_fix",
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
        Analyzes a state containing a failing test and generates a patch.

        Args:
            state: The current state, expected to contain 'failing_test_info'.
                   'failing_test_info': {
                       'test_file_path': str,
                       'test_code': str,
                       'error_message': str,
                       'source_file_path': str,
                       'source_code': str
                   }

        Returns:
            A proposal containing a patch to fix the bug.
        """
        bug_info = state.get("failing_test_info")
        if not bug_info:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.FAILED, reason="No failing test info found in state.")

        # 1. Run static analysis for more context (placeholder)
        static_issues = ops.run_static_analysis(bug_info["source_code"])
        # In a real system, these issues might be added to the prompt.

        # 2. Generate a patch using the LLM
        prompt_spec = prompts.get_prompt("generate_patch")
        formatted_prompt = prompt_spec.format(
            file_path=bug_info["source_file_path"],
            source_code=bug_info["source_code"],
            test_file_path=bug_info["test_file_path"],
            test_code=bug_info["test_code"],
            test_error=bug_info["error_message"]
        )

        llm_response = await self.llm_client.complete({"prompt": formatted_prompt})

        try:
            patch = ops.extract_diff_from_llm(llm_response["content"])
            return Proposal(
                agent_id=self.agent_id,
                data={"patch": patch, "bug_info": bug_info},
                status=Status.SUCCESS
            )
        except ops.PatchError as e:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.FAILED, reason=f"Failed to generate patch: {e}")

    def validate_proposal(self, proposal: Proposal) -> bool:
        """
        Validates the proposed patch.

        In a real system, this would be a complex process:
        1. Create a temporary sandbox environment.
        2. Apply the patch to the source code.
        3. Re-run the specific failing test.
        4. If the test passes and no other tests regress, the patch is valid.

        For this simulation, we will perform a simple structural validation.
        """
        if proposal.status != Status.SUCCESS or "patch" not in proposal.data:
            return False

        patch = proposal.data["patch"]
        if not isinstance(patch, str) or not patch:
            return False

        # Check if it looks like a diff
        if not patch.startswith("---") and not patch.startswith("+++"):
             print(f"Patch validation failed: Does not look like a diff.")
             return False

        print("Patch validation successful (simulated).")
        return True

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the proposal by calculating the dynamic energy reduction from fixing a bug.
        """
        patch = proposal.data["patch"]
        bug_info = proposal.data["bug_info"]

        # 1. Calculate the reduction in dynamic energy.
        # Fixing a failing test reduces the system's error state, thus lowering dynamic energy.
        # We can model this as a fixed energy reduction per bug fixed.
        error_reduction_value = 1.0 # One bug fixed

        # This metric can be used by the energy calculator
        dynamic_metrics = {
            "errors_fixed": error_reduction_value
        }

        # We assume the calculator can handle this metric.
        # Let's calculate a simple negative energy impact.
        # The weight `w_error_reduction` would be defined in the calculator's config.
        energy_reduction = self.energy_calculator.config.get("w_error_reduction", 5.0) * error_reduction_value

        # 2. Create the action
        action_data = {
            "file_to_patch": bug_info["source_file_path"],
            "patch": patch,
            "energy_impact": {
                # This is an energy *reduction*
                "dynamic": -energy_reduction
            }
        }

        return Action(
            agent_id=self.agent_id,
            data=action_data,
            status=Status.SUCCESS
        )
