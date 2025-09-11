"""
Operations for the TunnelFix Agent.
"""
import json

class OptimizationError(Exception):
    """Custom exception for optimization errors."""
    pass

def parse_optimization_proposal(llm_output: str) -> str:
    """
    Parses the JSON output from the LLM into a string containing the
    refactored code.
    """
    try:
        data = json.loads(llm_output)
        if "refactored_code" not in data or not isinstance(data["refactored_code"], str):
            raise OptimizationError("LLM output is missing 'refactored_code' string.")
        return data["refactored_code"]
    except json.JSONDecodeError:
        raise OptimizationError("Failed to decode LLM output as JSON.")


import math
import Levenshtein
from agents.base import ops as base_ops

def calculate_barrier_width(code: str) -> float:
    """
    Calculates the "width" of the performance barrier, proxied by
    cyclomatic complexity. A higher complexity represents a wider barrier
    that is harder to tunnel through. We use a log scale to keep the
    value in a manageable range.
    """
    try:
        ast = base_ops.parse_to_ast(code)
        complexity = base_ops.calculate_cyclomatic_complexity(ast)
        return math.log1p(complexity)
    except Exception:
        # If parsing fails, assume a moderate barrier width
        return math.log1p(10)

def calculate_kappa(original_code: str, refactored_code: str) -> float:
    """
    Calculates kappa. In quantum tunneling, kappa is related to the
    particle's energy and the barrier height. A more "energetic" refactoring
    (a larger change) should have a better chance of tunneling, which
    corresponds to a lower kappa value.
    """
    distance = Levenshtein.distance(original_code, refactored_code)
    if distance == 0:
        # An infinite kappa means zero probability of tunneling, as no change occurs.
        return float('inf')
    # Kappa is inversely proportional to the magnitude of the change.
    return 1.0 / math.log1p(distance)

def calculate_tunneling_probability(kappa: float, barrier_width: float) -> float:
    """
    Calculates the probability of a refactoring "tunneling" through a
    performance barrier, based on the formula T ∝ exp(-2 * kappa * d).
    A lower kappa (more significant change) or a lower barrier_width
    (less complex code) increases the probability.
    """
    # Scaling constant to tune the sensitivity of the probability.
    scaling_constant = 0.1
    exponent = -2 * scaling_constant * kappa * barrier_width

    return math.exp(exponent)
