"""
FluctuaTest Agent: Assesses system stability by running simulated
chaos experiments.
"""
from typing import Dict, Any, Optional

from agents.base.agent import QuantumAgent
from core.state_space import StateSpace
from core.energy_calculator import EnergyCalculator
from core.data_models import AgentTask as Proposal, QCState as State, AgentResult as Action, Status
from monitoring.metrics import QuantumMetrics as MetricsLogger
from agents.base.policies import PolicyEngine
from agents.base.memory import AgentMemory
from llm.client import LLMClient

from . import prompts
from . import ops

class FluctuaTestAgent(QuantumAgent):
    """
    The FluctuaTest Agent is a chaos engineering specialist.
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
            name="fluctuatest",
            state_space=state_space,
            energy_calculator=energy_calculator,
            metrics_logger=metrics_logger,
            policy_engine=policy_engine,
            agent_memory=agent_memory,
            agent_id=agent_id,
        )
        self.llm_client = llm_client
        self.simulator = ops.ChaosSimulator()

    async def analyze_state(self, state: State) -> Proposal:
        """
        Analyzes the system and proposes a chaos experiment.
        """
        # For now, we'll just propose a generic experiment
        component_description = "The main API gateway"
        prompt = prompts.get_prompt("generate_chaos_experiment").format(component_description=component_description)

        response = await self.llm_client.complete({"prompt": prompt})

        try:
            experiment = ops.parse_chaos_experiment_proposal(response["content"])
        except ops.ChaosExperimentError as e:
            return Proposal(agent_name=self.name, task_type="chaos_test", payload={}, status=Status.FAILED, reason=str(e))

        return Proposal(
            agent_name=self.name,
            task_type="chaos_test",
            payload={"experiment": experiment},
            status=Status.SUCCESS
        )

    def validate_proposal(self, proposal: Proposal) -> bool:
        """
        Validates the chaos experiment proposal.
        """
        if proposal.status != Status.SUCCESS:
            return False
        return "experiment" in proposal.payload

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the chaos experiment and calculates the energy impact.
        """
        experiment = proposal.payload.get("experiment")
        if not experiment:
            return Action(task_id=proposal.id, agent_name=self.name, action_taken=False, status=Status.FAILED, error="No experiment in proposal.")

        # Get the current state from the quantum context
        initial_state = proposal.quantum_context
        if not initial_state:
            return Action(task_id=proposal.id, agent_name=self.name, action_taken=False, status=Status.FAILED, error="No initial state in proposal context.")

        # Run the simulation
        final_state = self.simulator.run_experiment(initial_state, experiment)

        # Assess stability
        energy_delta = final_state.energy - initial_state.energy
        is_stable = energy_delta < self.energy_calculator.config.get("stability_threshold", 50.0)

        # The "debt" energy increases if the system is unstable
        debt_energy_impact = 0.0
        if not is_stable:
            debt_energy_impact = energy_delta # Penalize by the amount of instability

        action_data = {
            "experiment": experiment,
            "is_stable": is_stable,
            "energy_delta": energy_delta,
            "energy_impact": {
                "debt": debt_energy_impact
            }
        }

        return Action(
            task_id=proposal.id,
            agent_name=self.name,
            action_taken=True,
            status=Status.SUCCESS,
            result=action_data
        )
