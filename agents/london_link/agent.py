import networkx as nx
from typing import Dict, Any, Optional
import itertools

from agents.base.agent import QuantumAgent
from core.state_space import StateSpace
from core.energy_calculator import EnergyCalculator
from core.types import Proposal, State, Action, Status
from monitoring.metrics import QuantumMetrics as MetricsLogger
from agents.base.policies import PolicyEngine
from agents.base.memory import AgentMemory
from llm.client import LLMClient
from agents.base import ops as base_ops

from . import prompts
from . import ops

class LondonLinkAgent(QuantumAgent):
    """
    The LondonLink Agent is an internal dependency optimization specialist.
    It uses an analogy to London dispersion forces to find and resolve
    improper couplings between distant modules in the codebase.
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
        all_source_files = state.metadata.get("source_code_map", {})
        if not all_source_files or len(all_source_files) < 2:
            return Proposal(agent_name=self.name, task_type="dependency_optimization", payload={}, reason="Not enough source files to analyze.")

        dep_graph = ops.build_dependency_graph(all_source_files)
        undirected_graph = dep_graph.graph.to_undirected()

        # Pre-calculate complexities to avoid redundant work
        complexities = {
            path: base_ops.calculate_cyclomatic_complexity(base_ops.parse_to_ast(code))
            for path, code in all_source_files.items()
        }

        module_path_map = {path.replace('/', '.').replace('.py', ''): path for path in all_source_files.keys()}

        most_attractive_pair = None
        lowest_potential = 0

        for mod1, mod2 in itertools.combinations(dep_graph.graph.nodes(), 2):
            if not nx.has_path(undirected_graph, mod1, mod2):
                continue

            # r = distance
            r = nx.shortest_path_length(undirected_graph, mod1, mod2)

            path1 = module_path_map.get(mod1)
            path2 = module_path_map.get(mod2)

            if not path1 or not path2: continue

            # C6 = polarizability constant, proxied by product of complexities
            c6 = complexities.get(path1, 1) * complexities.get(path2, 1)

            potential = ops.calculate_attraction_potential(r, c6)

            if potential < lowest_potential:
                lowest_potential = potential
                most_attractive_pair = (mod1, mod2)

        if not most_attractive_pair:
            return Proposal(agent_name=self.name, task_type="dependency_optimization", payload={}, reason="No coupled modules found to optimize.")

        prompt_spec = prompts.get_prompt("refactor_coupled_modules")
        formatted_prompt = prompt_spec.format(module_a=most_attractive_pair[0], module_b=most_attractive_pair[1])
        llm_response = await self.llm_client.complete({"prompt": formatted_prompt})

        try:
            plan = ops.parse_refactoring_proposal(llm_response["content"])
            plan["original_potential"] = lowest_potential
            return Proposal(
                agent_name=self.name,
                task_type="dependency_optimization",
                payload={"optimization_plan": plan},
                status=Status.SUCCESS,
            )
        except ops.LondonLinkError as e:
            return Proposal(agent_name=self.name, task_type="dependency_optimization", payload={}, status=Status.FAILED, reason=str(e))


    def validate_proposal(self, proposal: Proposal) -> bool:
        if proposal.status != Status.SUCCESS: return False
        if not proposal.payload: return True
        plan = proposal.payload.get("optimization_plan", {})
        return all(k in plan for k in ["refactored_module_path", "refactored_code", "explanation"])

    def execute(self, proposal: Proposal) -> Action:
        plan = proposal.payload.get("optimization_plan")
        if not plan:
            return Action(task_id=proposal.id, agent_name=self.name, action_taken=False)

        # The energy reduction is the change in potential energy.
        # A successful refactoring should bring the potential closer to 0.
        # So, energy reduction = 0 - original_potential
        original_potential = plan.get("original_potential", 0)
        energy_reduction = -original_potential

        action_data = {
            "optimization_plan": plan,
            "energy_impact": { "interaction": -energy_reduction }
        }

        return Action(
            task_id=proposal.id,
            agent_name=self.name,
            action_taken=True,
            result=action_data,
            status=Status.SUCCESS
        )
