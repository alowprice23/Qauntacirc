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

        proposals = []
        for file_path, content in code_files.items():
            if not file_path.startswith("src/"):
                continue

            # 1. Propose an optimization via LLM
            prompt = prompts.get_prompt("generate_optimization").format(code_block=content)
            response = await self.llm_client.complete({"prompt": prompt})

            try:
                refactored_code = ops.parse_optimization_proposal(response["content"])
            except ops.OptimizationError:
                continue

            # 2. Calculate the physics-based properties of the proposal
            barrier_width = ops.calculate_barrier_width(content)
            kappa = ops.calculate_kappa(content, refactored_code)
            tunneling_prob = ops.calculate_tunneling_probability(kappa, barrier_width)

            # 3. Benchmark the performance to see if the optimization is valid
            baseline_perf = self.benchmark.run(content)
            optimized_perf = self.benchmark.run(refactored_code)
            perf_improvement = baseline_perf - optimized_perf

            # We only consider successful optimizations
            if perf_improvement > 0:
                proposals.append({
                    "file_path": file_path,
                    "original_code": content,
                    "refactored_code": refactored_code,
                    "performance_improvement": perf_improvement,
                    "tunneling_probability": tunneling_prob,
                })

        # 4. Select the best proposal based on tunneling probability
        if not proposals:
            return Proposal(agent_name=self.name, task_type="optimization", payload={}, status=Status.SUCCESS, reason="No viable optimizations found.")

        best_proposal = max(proposals, key=lambda p: p["tunneling_probability"])

        return Proposal(
            agent_name=self.name,
            task_type="optimization",
            payload={"optimizations": {best_proposal["file_path"]: best_proposal}},
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
        The energy reduction is scaled by the performance improvement and the
        tunneling probability, rewarding high-risk, high-reward optimizations.
        """
        optimizations = proposal.payload.get("optimizations", {})
        if not optimizations:
            return Action(task_id=proposal.id, agent_name=self.name, action_taken=False, status=Status.SUCCESS, result={})

        # Since we only have one optimization, we can get it directly
        best_optimization = list(optimizations.values())[0]
        perf_improvement = best_optimization.get("performance_improvement", 0)
        tunneling_prob = best_optimization.get("tunneling_probability", 0)

        # Debt energy reduction is scaled by performance and probability
        debt_energy_reduction = -1 * perf_improvement * tunneling_prob * self.energy_calculator.config.get("w_performance", 100.0)

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
