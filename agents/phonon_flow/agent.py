# agents/phonon_flow/agent.py
"""
PhononFlow Agent: Optimizes code structure to improve information flow.

This agent analyzes the structural properties of the codebase, such as
coupling and complexity, and proposes refactorings to improve the "speed of
sound" (maintainability) of the code.
"""
import json
from typing import Dict, Any, Optional

from agents.base.agent import QuantumAgent
from core.state_space import StateSpace
from core.energy_calculator import EnergyCalculator
from core.types import Proposal, State, Action, Status
from monitoring.metrics import QuantumMetrics as MetricsLogger
from agents.base.policies import PolicyEngine
from agents.base.memory import AgentMemory
from llm.client import LLMClient

from . import prompts
from . import ops

class PhononFlowAgent(QuantumAgent):
    """
    The PhononFlow Agent is a software architect focused on structural quality.

    It uses the physics of phonons (lattice vibrations) as an analogy for how
    changes propagate through a codebase. Its goal is to refactor code to
    increase the "speed of sound" (v_s), making the code more maintainable.
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
        Analyzes the codebase to find the component with the worst "speed of
        sound" and proposes a refactoring to improve it.
        """
        all_source_files = state.metadata.get("source_code_map", {})
        if not all_source_files:
            return Proposal(agent_name=self.name, task_type="refactoring", payload={}, reason="No source code to analyze.")

        # 1. Build dependency graph
        dep_graph = ops.build_dependency_graph(all_source_files)

        # 2. Find the "slowest" file in the codebase
        slowest_file = None
        lowest_vs = float('inf')

        for file_path, code in all_source_files.items():
            module_name = file_path.replace('/', '.').replace('.py', '')
            if module_name not in dep_graph.graph:
                continue

            coupling = dep_graph.graph.in_degree(module_name) + dep_graph.graph.out_degree(module_name)
            density = ops.calculate_complexity_density(code)
            vs = ops.calculate_speed_of_sound(coupling, density)

            if vs < lowest_vs:
                lowest_vs = vs
                slowest_file = {"path": file_path, "code": code}

        if not slowest_file:
            return Proposal(agent_name=self.name, task_type="refactoring", payload={}, reason="Could not identify a file to refactor.")

        # 3. Generate a refactoring proposal for the slowest file
        prompt_spec = prompts.get_prompt("refactor_for_decoupling")
        formatted_prompt = prompt_spec.format(file_path=slowest_file["path"], code_block=slowest_file["code"])
        llm_response = await self.llm_client.complete({"prompt": formatted_prompt})

        try:
            proposal_data = ops.parse_refactoring_proposal(llm_response["content"])
            proposal_data["file_to_update"] = slowest_file["path"]

            return Proposal(
                agent_name=self.name,
                task_type="refactoring",
                payload=proposal_data,
                status=Status.SUCCESS,
            )
        except ops.PhononFlowError as e:
            return Proposal(agent_name=self.name, task_type="refactoring", payload={}, status=Status.FAILED, reason=f"Failed to generate refactoring plan: {e}")

    def validate_proposal(self, proposal: Proposal) -> bool:
        """Validates the refactoring proposal."""
        if proposal.status != Status.SUCCESS:
            return False
        if not proposal.payload:
            return True # No-op is valid

        return "refactored_code" in proposal.payload and "file_to_update" in proposal.payload

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the proposal by calculating the interaction energy reduction based
        on the quality of the proposed refactoring.
        """
        if not proposal.payload:
            return Action(task_id=proposal.id, agent_name=self.name, action_taken=False, status=Status.SUCCESS, result={})

        refactored_code = proposal.payload["refactored_code"]

        # Heuristic: Interaction energy reduction is proportional to the "quality"
        # (speed of sound) of the newly proposed code.
        # We assume coupling remains similar for this heuristic, and just measure density.
        new_density = ops.calculate_complexity_density(refactored_code)

        # Assume average coupling for the heuristic calculation of v_s
        new_vs = ops.calculate_speed_of_sound(coupling=5.0, density=new_density)

        # The energy of the change is analogous to h-bar * omega = h-bar * v_s * k
        # We'll treat "k" (wavenumber) as a constant, so energy is proportional to v_s.
        w_maintainability = self.energy_calculator.config.get("w_maintainability", 5.0)
        energy_reduction = w_maintainability * new_vs

        action_data = {
            "refactoring_plan": proposal.payload,
            "energy_impact": {
                "interaction": -energy_reduction
            }
        }

        return Action(
            task_id=proposal.id,
            agent_name=self.name,
            action_taken=True,
            result=action_data,
            status=Status.SUCCESS
        )
