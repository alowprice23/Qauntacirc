"""
TunnelFix Agent: Optimizes code performance by "tunneling" through
performance barriers.
"""
from typing import Dict, Any, Optional

from agents.base.agent import QuantumAgent
from core.state_space import StateSpace
from core.energy_calculator import EnergyCalculator
from core.types import AgentTask as Proposal, QCState as State, AgentResult as Action, Status
from monitoring.metrics import QuantumMetrics as MetricsLogger
from agents.base.policies import PolicyEngine
from agents.base.memory import AgentMemory
from llm.client import LLMClient

from . import prompts
from . import ops
from .benchmark import MockBenchmark

class TunnelFixAgent(QuantumAgent):
    """
    The TunnelFix Agent is a performance optimization specialist.
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
            name="tunnelfix",
            state_space=state_space,
            energy_calculator=energy_calculator,
            metrics_logger=metrics_logger,
            policy_engine=policy_engine,
            agent_memory=agent_memory,
            agent_id=agent_id,
        )
        self.llm_client = llm_client
        self.benchmark = MockBenchmark()

    async def analyze_state(self, state: State) -> Proposal:
        """
        Analyzes code for performance bottlenecks and proposes optimizations.
        """
        schrodinger_dev_output = state.metadata.get("schrodinger_dev_output", {})
        code_files = schrodinger_dev_output.get("files_to_create", {})

        if not code_files:
            return Proposal(agent_name=self.name, task_type="optimization", payload={}, status=Status.SUCCESS, reason="No code files to analyze.")

        optimizations = {}
        for file_path, content in code_files.items():
            if file_path.startswith("src/"):
                # 1. Get baseline performance
                baseline_perf = self.benchmark.run(content)

                # 2. Propose optimization
                prompt = prompts.get_prompt("generate_optimization").format(code_block=content)
                response = await self.llm_client.complete({"prompt": prompt})

                try:
                    refactored_code = ops.parse_optimization_proposal(response["content"])
                except ops.OptimizationError:
                    continue

                # 3. "Verify" optimization
                optimized_perf = self.benchmark.run(refactored_code)

                if optimized_perf < baseline_perf:
                    optimizations[file_path] = {
                        "original_code": content,
                        "refactored_code": refactored_code,
                        "performance_improvement": baseline_perf - optimized_perf,
                    }

        return Proposal(
            agent_name=self.name,
            task_type="optimization",
            payload={"optimizations": optimizations},
            status=Status.SUCCESS
        )

    def validate_proposal(self, proposal: Proposal) -> bool:
        """
        Validates the optimization proposal.
        """
        if proposal.status != Status.SUCCESS:
            return False
        return "optimizations" in proposal.payload

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the proposal by calculating the energy impact of the optimization.
        """
        optimizations = proposal.payload.get("optimizations", {})
        total_perf_improvement = sum(opt["performance_improvement"] for opt in optimizations.values())

        # Debt energy reduction is proportional to performance improvement
        debt_energy_reduction = -total_perf_improvement * self.energy_calculator.config.get("w_performance", 100.0)

        action_data = {
            "optimizations": optimizations,
            "energy_impact": {
                "debt": debt_energy_reduction
            }
        }

        return Action(
            task_id=proposal.id,
            agent_name=self.name,
            action_taken=True,
            status=Status.SUCCESS,
            result=action_data
        )
