"""
Distance metrics for QuantaCirc state objects.
"""
from typing import TYPE_CHECKING
import numpy as np
from Levenshtein import distance as levenshtein_distance

if TYPE_CHECKING:
    from core.types import QCState

def calculate_state_distance(state1: "QCState", state2: "QCState") -> float:
    """
    Calculates a distance between two QCState objects.

    This is a simplified metric for simulation purposes. A real implementation
    would involve a more sophisticated weighted sum of edit distances, graph
    distances, and test vector distances as described in the README.md.

    Args:
        state1: The first state.
        state2: The second state.

    Returns:
        A float representing the distance between the two states.
    """
    # 1. Energy difference
    energy_dist = abs(state1.energy - state2.energy)

    # 2. Module content difference (using Levenshtein distance)
    module_dist = 0.0
    if state1.modules and state2.modules:
        # For simplicity, compare the first module
        module_dist = levenshtein_distance(state1.modules[0], state2.modules[0])

    # Combine the distances (simple weighted sum)
    # The weights are chosen to give a reasonable scale for the simulation.
    distance = 0.1 * energy_dist + 0.9 * module_dist

    return distance