"""
HydroSpread Agent: Forecasts code growth based on hydrodynamic principles.
"""
from typing import Dict, Any, Optional, List

from agents.base.agent import QuantumAgent
from core.state_space import StateSpace
from core.energy_calculator import EnergyCalculator
from core.types import AgentTask as Proposal, QCState as State, AgentResult as Action, Status, TaskQuanta
from monitoring.metrics import QuantumMetrics as MetricsLogger
from agents.base.policies import PolicyEngine
from agents.base.memory import AgentMemory
from llm.client import LLMClient

from . import prompts
from . import ops

class HydroSpreadAgent(QuantumAgent):
    """
    The HydroSpread Agent is a project forecasting specialist.
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
            name="hydrospread",
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
        Analyzes the current project state and forecasts code growth.
        """
        planck_forge_output = state.metadata.get("planck_forge_output", {})
        tasks: List[TaskQuanta] = planck_forge_output.get("tasks", [])

        if not tasks:
            return Proposal(agent_name=self.name, task_type="forecast", payload={}, status=Status.SUCCESS, reason="No tasks to analyze.")

        # Get viscosity from the state (e.g., based on development friction)
        # This is a mock value for now
        viscosity = state.metadata.get("development_viscosity", 1.0)

        # Forecast for the next development cycle
        time_horizon = 1.0

        forecasted_size = ops.forecast_code_growth(tasks, viscosity, time_horizon)

        num_tasks = len(tasks)
        avg_energy = sum(t.energy for t in tasks) / num_tasks if num_tasks > 0 else 0

        prompt = prompts.get_prompt("generate_growth_forecast").format(
            num_tasks=num_tasks,
            avg_energy=avg_energy,
            viscosity=viscosity,
            forecasted_size=forecasted_size,
        )

        response = await self.llm_client.complete({"prompt": prompt})

        return Proposal(
            agent_name=self.name,
            task_type="forecast",
            payload={"forecast_report": response["content"]},
            status=Status.SUCCESS
        )

    def validate_proposal(self, proposal: Proposal) -> bool:
        """
        Validates the forecast proposal.
        """
        if proposal.status != Status.SUCCESS:
            return False
        return "forecast_report" in proposal.payload

    def execute(self, proposal: Proposal) -> Action:
        """
        This agent is advisory and does not directly impact the system's energy.
        """
        forecast_report = proposal.payload.get("forecast_report")

        action_data = {
            "forecast_report": forecast_report,
            "energy_impact": {} # No direct energy impact
        }

        return Action(
            task_id=proposal.id,
            agent_name=self.name,
            action_taken=True,
            status=Status.SUCCESS,
            result=action_data
        )
