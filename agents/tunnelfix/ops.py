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
