# agents/hydro_spread/agent.py
"""
HydroSpread Agent: Models and forecasts system growth and complexity evolution.

This agent analyzes historical trends to predict future complexity, allowing for
proactive architectural decisions.
"""
import asyncio
import json
import re
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

class HydroSpreadAgent(QuantumAgent):
    """
    The HydroSpread Agent is a quantitative analyst for software evolution.

    It uses historical data to model growth patterns and forecasts future
    increases in static energy (complexity), providing valuable insights for
    long-term strategic planning. Its rigor is Heuristic-Inspired.
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
            name="hydro_spread",
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
        Analyzes historical data and proposes a complexity forecast.

        Args:
            state: The current state, expected to contain 'historical_states'.

        Returns:
            A proposal containing a complexity forecast.
        """
        historical_states = state.get("historical_states", [])
        if len(historical_states) < 2:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.SUCCESS, reason="Not enough historical data to analyze.")

        # 1. Analyze growth patterns (simulated)
        summary = ops.analyze_growth_patterns(historical_states)

        # 2. Generate a forecast using the LLM
        prompt_spec = prompts.get_prompt("forecast_complexity")
        formatted_prompt = prompt_spec.format(historical_data_summary=summary)

        llm_response = await self.llm_client.complete({"prompt": formatted_prompt})

        try:
            forecast = ops.parse_complexity_forecast(llm_response["content"])
            return Proposal(
                agent_id=self.agent_id,
                data={"complexity_forecast": forecast},
                status=Status.SUCCESS
            )
        except ops.ForecastError as e:
            return Proposal(agent_id=self.agent_id, data={}, status=Status.FAILED, reason=f"Failed to generate forecast: {e}")

    def validate_proposal(self, proposal: Proposal) -> bool:
        """Validates the complexity forecast."""
        if proposal.status != Status.SUCCESS:
            return False

        if "complexity_forecast" not in proposal.data:
            return True

        try:
            ops.parse_complexity_forecast(json.dumps(proposal.data["complexity_forecast"]))
            return True
        except ops.ForecastError as e:
            print(f"Complexity forecast validation failed: {e}")
            return False

    def execute(self, proposal: Proposal) -> Action:
        """
        Executes the proposal by packaging the forecast. The energy impact is informational.
        """
        if "complexity_forecast" not in proposal.data:
            return Action(agent_id=self.agent_id, data={}, status=Status.SUCCESS)

        forecast = proposal.data["complexity_forecast"]

        # This agent's action is purely informational. It forecasts a future
        # energy change but doesn't cause one directly.
        # We can add the forecast to the action data.

        # A simple heuristic to quantify the forecast
        forecast_text = forecast.get("complexity_forecast", "")
        match = re.search(r'(\d+)%', forecast_text)
        if match:
            percent_increase = float(match.group(1))
        else:
            percent_increase = 0.0

        # This isn't a change to the current state's energy, but a prediction.
        predicted_static_energy_increase = self.energy_calculator.config.get("w_complexity", 1.0) * percent_increase

        action_data = {
            "forecast": forecast,
            "predicted_energy_impact": {
                "static": predicted_static_energy_increase
            }
        }

        return Action(
            agent_id=self.agent_id,
            data=action_data,
            status=Status.SUCCESS
        )
