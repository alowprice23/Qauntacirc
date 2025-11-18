# agents/bose_boost/agent.py
"""
BoseBoost Agent: Optimizes code performance by identifying and refactoring
bottlenecks.

This agent uses (simulated) profiling data to find inefficient code and
leverages an LLM to suggest algorithmic and structural improvements.
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

class BoseBoostAgent(QuantumAgent):
    """
    The BoseBoost Agent is a performance optimization specialist.

    It profiles the system's code to find hot spots and then generates
    refactoring proposals to improve performance, thereby reducing the
    system's dynamic energy.
    """
    def __init__(
        self,
        state_space: StateSpace,
        energy_calculator: EnergyCalculator,
        metrics_logger: MetricsLogger,
        policy_engine: PolicyEngine,
        agent_memory: AgentMemory,
        llm_client: LLMClient,
        config: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
    ):
        super().__init__(
            name="bose_boost",
            state_space=state_space,
            energy_calculator=energy_calculator,
            metrics_logger=metrics_logger,
            policy_engine=policy_engine,
            agent_memory=agent_memory,
            agent_id=agent_id,
        )
        self.llm_client = llm_client
        self.config = config or {}

    async def analyze_state(self, state: State) -> Proposal:
        """
        Analyzes the system's code, finds bottlenecks, and proposes optimizations.

        Args:
            state: The current state, containing a map of all source code files.

        Returns:
            A proposal containing optimization plans.
        """
        all_source_files = state.get("source_code_map", {})
        if not all_source_files:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.SUCCESS, reason="No source code to analyze.")

        # 1. Profile the code (simulated)
        profiling_data = ops.run_profiler(all_source_files)

        # 2. Identify bottlenecks
        bottlenecks = ops.identify_bottlenecks(profiling_data)
        if not bottlenecks:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.SUCCESS, reason="No performance bottlenecks found.")

        # 3. Generate optimization plans for each bottleneck
        plan_coros = []
        for bottleneck in bottlenecks:
            plan_coros.append(self._generate_optimization_plan(bottleneck))

        optimization_plans = await asyncio.gather(*plan_coros, return_exceptions=True)

        valid_plans = [p for p in optimization_plans if not isinstance(p, Exception)]

        return Proposal(
            agent_id=self.agent_id,
            data={"optimization_plans": valid_plans, "original_bottlenecks": bottlenecks},
            status=Status.SUCCESS
        )

    async def _generate_optimization_plan(self, bottleneck: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to generate an optimization plan for a single bottleneck."""
        profiling_summary = (
            f"Function '{bottleneck['function_name']}' is a bottleneck. "
            f"Execution time: {bottleneck['execution_time_ms']}ms. "
            f"Memory usage: {bottleneck['memory_usage_mb']}MB."
        )

        prompt_spec = prompts.get_prompt("optimize_code")
        formatted_prompt = prompt_spec.format(
            file_path=bottleneck["file_path"],
            code_block=bottleneck["code_block"],
            profiling_summary=profiling_summary
        )

        llm_response = await self.llm_client.complete({"prompt": formatted_prompt})
        plan = ops.parse_optimization_plan(llm_response["content"])
        return plan

    def validate_proposal(self, proposal: Proposal) -> bool:
        """
        Validates the optimization plans.

        A real implementation would check for semantic equivalence and run
        performance benchmarks. Here, we just validate the plan's structure.
        """
        if proposal.status != Status.SUCCESS:
            return False

        for plan in proposal.data.get("optimization_plans", []):
            try:
                ops.parse_optimization_plan(json.dumps(plan))
            except ops.OptimizationError as e:
                print(f"Optimization plan validation failed: {e}")
                return False

        return True

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the proposal by calculating the dynamic energy reduction.
        """
        optimization_plans = proposal.data.get("optimization_plans", [])
        bottlenecks = proposal.data.get("original_bottlenecks", [])

        # 1. Calculate the reduction in dynamic energy from performance improvements.
        total_time_reduction = 0
        for bottleneck in bottlenecks:
            # Assume the optimization is successful and reduces runtime by 50% (simulated)
            time_reduction = bottleneck.get("execution_time_ms", 0) * 0.5
            total_time_reduction += time_reduction

        # This metric can be used by the energy calculator
        dynamic_metrics = {
            "avg_response_time_reduction": total_time_reduction
        }

        # We assume the calculator can handle this metric.
        # Let's calculate a simple negative energy impact.
        # The weight `w_runtime_perf` is defined in the calculator.
        energy_reduction = self.energy_calculator.config.get("w_runtime_perf", 2.0) * total_time_reduction

        # 2. Create the action
        action_data = {
            "optimization_plans": optimization_plans,
            "energy_impact": {
                "dynamic": -energy_reduction
            }
        }

        return Action(
            agent_id=self.agent_id,
            data=action_data,
            status=Status.SUCCESS
        )
