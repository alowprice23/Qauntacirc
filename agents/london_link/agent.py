# agents/london_link/agent.py
"""
LondonLink Agent: Manages and optimizes external software dependencies.

This agent analyzes dependency files, scans for vulnerabilities, and proposes
optimizations to enhance security and maintainability.
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

class LondonLinkAgent(QuantumAgent):
    """
    The LondonLink Agent is a supply chain security specialist.

    It examines the project's dependencies to find and suggest fixes for
    vulnerabilities, outdated packages, and other risks, reducing the system's
    interaction energy.
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
            name="london_link",
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
        Analyzes dependency files and proposes optimizations.

        Args:
            state: The current state, expected to contain 'dependency_file_content'.

        Returns:
            A proposal containing a dependency optimization plan.
        """
        dependency_content = state.get("dependency_file_content")
        if not dependency_content:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.SUCCESS, reason="No dependency file content found.")

        # 1. Analyze the dependency file
        dependencies = ops.analyze_dependencies(dependency_content)

        # 2. Scan for vulnerabilities (simulated)
        vulnerability_report = ops.scan_for_vulnerabilities(dependencies)

        # 3. Generate an optimization plan using the LLM
        prompt_spec = prompts.get_prompt("optimize_dependencies")
        formatted_prompt = prompt_spec.format(
            dependency_list=dependency_content,
            vulnerability_report=vulnerability_report
        )

        llm_response = await self.llm_client.complete({"prompt": formatted_prompt})

        try:
            plan = ops.parse_optimization_plan(llm_response["content"])
            return Proposal(
                agent_id=self.agent_id,
                data={"optimization_plan": plan, "dependencies": dependencies},
                status=Status.SUCCESS
            )
        except ops.DependencyError as e:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.FAILED, reason=f"Failed to generate optimization plan: {e}")

    def validate_proposal(self, proposal: Proposal) -> bool:
        """Validates the dependency optimization plan."""
        if proposal.status != Status.SUCCESS:
            return False

        if "optimization_plan" not in proposal.data:
            return True

        try:
            # Check the structure of the plan
            plan = proposal.data["optimization_plan"]
            for item in plan:
                if not all(k in item for k in ["package", "current_version", "recommended_version", "reason"]):
                    return False
            return True
        except Exception as e:
            print(f"Dependency optimization plan validation failed: {e}")
            return False

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the proposal by generating an SBOM and calculating energy impact.
        """
        if "optimization_plan" not in proposal.data:
            return Action(agent_id=self.agent_id, data={}, status=Status.SUCCESS)

        plan = proposal.data["optimization_plan"]
        dependencies = proposal.data["dependencies"]

        # 1. Generate an SBOM
        sbom = ops.generate_sbom(dependencies)

        # 2. Calculate the reduction in interaction energy.
        # This is proportional to the number of critical issues fixed.
        vulnerabilities_fixed = 0
        for action in plan:
            if "vulnerability" in action["reason"].lower():
                vulnerabilities_fixed += 1

        energy_reduction = self.energy_calculator.config.get("w_vulnerability_fix", 20.0) * vulnerabilities_fixed

        # 3. Create the action
        action_data = {
            "optimization_plan": plan,
            "sbom": sbom,
            "energy_impact": {
                "interaction": -energy_reduction
            }
        }

        return Action(
            agent_id=self.agent_id,
            data=action_data,
            status=Status.SUCCESS
        )
