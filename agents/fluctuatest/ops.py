"""
Operations for the FluctuaTest Agent.
"""
import json
import random
from typing import Dict, Any
from core.types import QCState

class ChaosExperimentError(Exception):
    """Custom exception for chaos experiment errors."""
    pass

def parse_chaos_experiment_proposal(llm_output: str) -> Dict[str, Any]:
    """
    Parses the JSON output from the LLM into a chaos experiment proposal.
    """
    try:
        data = json.loads(llm_output)
        required_keys = ["hypothesis", "experiment_type", "magnitude", "duration_seconds"]
        if not all(key in data for key in required_keys):
            raise ChaosExperimentError("LLM output is missing required keys for the chaos experiment proposal.")
        return data
    except json.JSONDecodeError:
        raise ChaosExperimentError("Failed to decode LLM output as JSON.")

class ChaosSimulator:
    """
    Simulates the effects of chaos experiments on the system state.
    """
    def run_experiment(self, state: QCState, experiment: Dict[str, Any]) -> QCState:
        """
        Applies a chaos experiment to a copy of the state and returns the new state.
        """
        new_state = state.copy(deep=True)
        experiment_type = experiment.get("experiment_type")
        magnitude = experiment.get("magnitude")

        if experiment_type == "latency_injection":
            # Simulate latency by increasing the debt component of the energy
            new_state.energy_components.dynamic += float(magnitude)
        elif experiment_type == "error_injection":
            # Simulate errors by increasing the number of failing tests (and thus the potential)
            new_state.lyapunov_potential += float(magnitude)
        elif experiment_type == "resource_exhaustion":
            # Simulate resource exhaustion by increasing the complexity energy
            new_state.energy_components.static += float(magnitude)

        # Recalculate total energy
        new_state.energy = new_state.energy_components.total

        return new_state
