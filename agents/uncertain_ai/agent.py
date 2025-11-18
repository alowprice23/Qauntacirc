# agents/uncertain_ai/agent.py
"""
UncertainAI Agent: Manages uncertainty and risk by generating targeted tests.

This agent analyzes code for potential weaknesses, edge cases, and security
vulnerabilities, then generates specific test cases to mitigate those risks,
thereby reducing the system's dynamic energy (uncertainty).
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

class UncertainAIAgent(QuantumAgent):
    """
    The UncertainAI Agent is a risk-mitigation specialist.

    It quantifies the uncertainty of code artifacts and then actively works
    to reduce that uncertainty by using an LLM to discover risks and generate
    targeted, mitigating test cases.
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
            name="uncertain_ai",
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
        Analyzes code artifacts for uncertainty and generates mitigating tests.

        Args:
            state: The current state, containing code from SchrodingerDev.

        Returns:
            A proposal containing new test cases to reduce uncertainty.
        """
        schrodinger_dev_output = state.get("schrodinger_dev_output", {})
        code_files = schrodinger_dev_output.get("files_to_create", {})

        if not code_files:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.SUCCESS, reason="No code files to analyze.")

        analysis_coros = []
        for file_path, content in code_files.items():
            # We only analyze source code, not the tests themselves
            if file_path.startswith("src/"):
                analysis_coros.append(self._analyze_code_file(content))

        results = await asyncio.gather(*analysis_coros, return_exceptions=True)

        all_new_tests = []
        total_uncertainty_reduction = 0
        for result in results:
            if isinstance(result, Exception):
                # Log the error but don't fail the whole proposal
                print(f"Error analyzing a file: {result}")
                continue
            all_new_tests.extend(result["new_tests"])
            total_uncertainty_reduction += result["uncertainty_reduction"]

        return Proposal(
            agent_id=self.agent_id,
            data={
                "newly_generated_tests": all_new_tests,
                "total_uncertainty_reduction": total_uncertainty_reduction
            },
            status=Status.SUCCESS
        )

    async def _analyze_code_file(self, code_content: str) -> Dict[str, Any]:
        """Helper to analyze a single code file for risks and generate tests."""
        # 1. Quantify initial uncertainty
        complexity = base_ops.calculate_cyclomatic_complexity(base_ops.parse_to_ast(code_content))
        initial_metrics = {'cyclomatic_complexity': float(complexity), 'llm_confidence': 0.9} # Assume confidence
        initial_uncertainty = ops.quantify_uncertainty(initial_metrics)

        # 2. Identify risks with the LLM
        risk_prompt = prompts.get_prompt("identify_risks").format(
            code_block=code_content,
            code_description="A component of the system under development."
        )
        risk_response = await self.llm_client.complete({"prompt": risk_prompt})
        identified_risks = ops.parse_identified_risks(risk_response["content"])

        if not identified_risks:
            return {"new_tests": [], "uncertainty_reduction": 0}

        # 3. Generate new tests for each risk
        test_gen_coros = []
        for risk in identified_risks:
            test_gen_coros.append(self._generate_test_for_risk(code_content, risk))

        new_tests = await asyncio.gather(*test_gen_coros)

        # 4. Quantify new uncertainty
        # The new uncertainty is lower because we now have more tests (implicitly)
        final_metrics = {
            'cyclomatic_complexity': float(complexity),
            'llm_confidence': 0.9,
            'num_identified_risks': 0 # The risks are now covered
        }
        final_uncertainty = ops.quantify_uncertainty(final_metrics)

        return {
            "new_tests": new_tests,
            "uncertainty_reduction": initial_uncertainty - final_uncertainty
        }

    async def _generate_test_for_risk(self, code: str, risk: str) -> str:
        """Helper to generate a single test case for a given risk."""
        prompt = prompts.get_prompt("generate_test_cases").format(
            code_block=code,
            risk_description=risk
        )
        response = await self.llm_client.complete({"prompt": prompt})
        return ops.extract_python_code(response["content"])

    def validate_proposal(self, proposal: Proposal) -> bool:
        """Validates the generated test cases."""
        if proposal.status != Status.SUCCESS:
            return False

        for test_code in proposal.data.get("newly_generated_tests", []):
            try:
                base_ops.parse_to_ast(test_code)
            except Exception as e:
                print(f"Generated test case has a syntax error: {e}")
                return False
        return True

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the proposal by calculating the dynamic energy reduction.
        """
        uncertainty_reduction = proposal.data.get("total_uncertainty_reduction", 0)

        # Dynamic energy change is the reduction in uncertainty.
        # A positive reduction in uncertainty leads to a negative change in energy.
        dynamic_energy_change = -uncertainty_reduction * self.energy_calculator.config.get("w_uncertainty", 10.0)

        action_data = {
            "new_test_cases": proposal.data["newly_generated_tests"],
            "energy_impact": {
                "dynamic": dynamic_energy_change
            }
        }

        return Action(
            agent_id=self.agent_id,
            data=action_data,
            status=Status.SUCCESS
        )
