# agents/schrodinger_dev/agent.py
"""
SchrodingerDev Agent: Generates code and proof skeletons from formal tasks.

This agent takes the formal task specifications from PlanckForge and uses
template-driven, LLM-based synthesis to generate initial code structures
and corresponding test/proof skeletons.
"""
import asyncio
from typing import Dict, Any, Optional, List

from agents.base.agent import QuantumAgent
from agents.base import ops as base_ops
from core.state_space import StateSpace
from core.energy_calculator import EnergyCalculator
from core.types import Proposal, State, Action, Status
from monitoring.metrics import MetricsLogger
from agents.base.policies import PolicyEngine
from agents.base.memory import AgentMemory
from llm.client import LLMClient

from . import prompts
from . import ops

class SchrodingerDevAgent(QuantumAgent):
    """
    The SchrodingerDev Agent generates code to satisfy formal requirements.

    It operates on the task graph produced by PlanckForge, generating a
    code skeleton and a proof skeleton for each task node. Its rigor is
    Empirically-Validated, meaning the quality of its output is assessed
    based on metrics and successful compilation/testing downstream.
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
            name="schrodinger_dev",
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
        Analyzes a state containing a task DAG from PlanckForge.

        Args:
            state: The current state, expected to have a 'task_dag' field.

        Returns:
            A proposal containing generated code and proof skeletons.
        """
        if "task_dag" not in state or "tasks" not in state.get("planck_forge_output", {}):
            return Proposal(agent_id=self.agent_id, data={}, status=Status.FAILED, reason="Task DAG or task list not found in state.")

        tasks = state["planck_forge_output"]["tasks"]
        generated_files = {}
        llm_confidence_scores = []

        # Process each task to generate code and proof skeletons
        generation_coros = []
        for task in tasks:
            generation_coros.append(self._generate_for_task(task))

        results = await asyncio.gather(*generation_coros, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                return Proposal(agent_id=self.agent_id, data={}, status=Status.FAILED, reason=f"Failed to generate code: {result}")

            generated_files.update(result["file_map"])
            llm_confidence_scores.append(result["confidence"])

        avg_confidence = sum(llm_confidence_scores) / len(llm_confidence_scores) if llm_confidence_scores else 0

        return Proposal(
            agent_id=self.agent_id,
            data={"generated_files": generated_files, "avg_llm_confidence": avg_confidence},
            status=Status.SUCCESS
        )

    async def _generate_for_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to generate code and proof for a single task."""
        task_id = task["task_id"]
        desc = task["description"]
        ver_criteria = task["verification_criteria"]

        # Generate code skeleton
        code_prompt = prompts.get_prompt("generate_code").format(
            task_description=desc,
            verification_criteria=ver_criteria,
            template_name="default" # Placeholder
        )
        code_response = await self.llm_client.complete({"prompt": code_prompt})
        code_skeleton = ops.extract_python_code(code_response["content"])
        ops.validate_python_syntax(code_skeleton)

        # Generate proof skeleton
        proof_prompt = prompts.get_prompt("generate_proof").format(
            task_description=desc,
            verification_criteria=ver_criteria
        )
        proof_response = await self.llm_client.complete({"prompt": proof_prompt})
        proof_skeleton = ops.extract_python_code(proof_response["content"])
        ops.validate_python_syntax(proof_skeleton)

        file_map = ops.create_code_and_proof_files(code_skeleton, proof_skeleton, task_id)

        # Assume confidence is part of the response as per llm/Plan.md
        confidence = (code_response.get("confidence", 0.9) + proof_response.get("confidence", 0.9)) / 2

        return {"file_map": file_map, "confidence": confidence}


    def validate_proposal(self, proposal: Proposal) -> bool:
        """
        Validates the generated code skeletons in the proposal.
        """
        if proposal.status != Status.SUCCESS or "generated_files" not in proposal.data:
            return False

        try:
            for file_path, content in proposal.data["generated_files"].items():
                if file_path.endswith(".py"):
                    ops.validate_python_syntax(content)
            return True
        except ops.CodeGenerationError as e:
            print(f"Proposal validation failed for agent {self.name}: {e}")
            return False

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the proposal by calculating the energy of the generated code.
        """
        generated_files = proposal.data["generated_files"]

        # 1. Calculate static energy from code complexity
        total_complexity = 0
        for content in generated_files.values():
            try:
                # Using the shared ops from the base agent
                ast_tree = base_ops.parse_to_ast(content)
                total_complexity += base_ops.calculate_cyclomatic_complexity(ast_tree)
            except Exception:
                # Ignore files that are not valid python or fail parsing
                continue

        static_metrics = {'cyclomatic_complexity': float(total_complexity)}
        static_energy = self.energy_calculator.compute_static_energy(static_metrics)

        # 2. Calculate dynamic energy from code generation quality (LLM confidence)
        # We model low confidence as contributing to higher dynamic energy
        avg_confidence = proposal.data.get("avg_llm_confidence", 0.5)
        quality_metric = (1.0 - avg_confidence) * 100 # Scale to be a significant number

        dynamic_metrics = {'code_generation_quality': quality_metric}
        # Assuming energy_calculator can be extended or uses a flexible key system
        # For now, let's manually calculate a simple dynamic energy component
        dynamic_energy = self.energy_calculator.config.get("w_code_quality", 1.0) * quality_metric

        # 3. Create the action
        action_data = {
            "files_to_create": generated_files,
            "energy_impact": {
                "static": static_energy,
                "dynamic": dynamic_energy,
            }
        }

        return Action(
            agent_id=self.agent_id,
            data=action_data,
            status=Status.SUCCESS
        )
