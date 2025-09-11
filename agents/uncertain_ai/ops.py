# agents/uncertain_ai/ops.py
"""
Operations for the UncertainAI Agent.

This module provides utilities for quantifying uncertainty in code, parsing
risk analysis from LLMs, and extracting generated test cases.
"""

import json
import re
import math
from typing import Dict, Any, List

class RiskAnalysisError(Exception):
    """Custom exception for errors during risk analysis."""
    pass

def calculate_risk_bound(num_tests: int, epsilon: float = 0.05) -> float:
    """
    Calculates an upper bound on the failure probability using a Chernoff-like bound.
    """
    if num_tests == 0:
        return 1.0 # Maximum uncertainty

    # P(error) <= exp(-2 * n * epsilon^2)
    bound = math.exp(-2 * num_tests * epsilon**2)
    return bound

def quantify_uncertainty(metrics: Dict[str, float], num_tests: int) -> float:
    """
    Quantifies the uncertainty of a code artifact based on various metrics
    and the number of tests.
    """
    # Base uncertainty from risk bound
    risk_bound = calculate_risk_bound(num_tests)

    # Other metrics can modulate the score
    w_complexity = 0.2
    w_confidence = 0.2

    complexity = metrics.get('cyclomatic_complexity', 0)
    llm_confidence = metrics.get('llm_confidence', 1.0)

    norm_complexity = min(complexity / 20.0, 1.0)
    inv_confidence = 1.0 - llm_confidence

    # Combine risk bound with other metrics
    uncertainty_score = (
        0.6 * risk_bound +
        w_complexity * norm_complexity +
        w_confidence * inv_confidence
    )

    return max(0.0, min(1.0, uncertainty_score))


def parse_identified_risks(llm_output: str) -> List[str]:
    """
    Parses the JSON output from the risk identification prompt.
    """
    try:
        # A more robust way to find the JSON object in the string
        json_match = re.search(r'{\s*"identified_risks":\s*\[.*?\]\s*}', llm_output, re.DOTALL)
        if not json_match:
            raise RiskAnalysisError("No valid JSON object found in the LLM output.")

        data = json.loads(json_match.group(0))

        if "identified_risks" not in data or not isinstance(data["identified_risks"], list):
            raise RiskAnalysisError("LLM output is missing 'identified_risks' list.")
        return data["identified_risks"]
    except json.JSONDecodeError:
        raise RiskAnalysisError("Failed to decode LLM output as JSON.")


def extract_python_code(llm_output: str) -> str:
    """
    Extracts a Python code block from the LLM's markdown-formatted output.
    """
    match = re.search(r"```python\n(.*?)```", llm_output, re.DOTALL)
    if match:
        return match.group(1).strip()

    match = re.search(r"```\n(.*?)```", llm_output, re.DOTALL)
    if match:
        return match.group(1).strip()

    print("Warning: No markdown block found in LLM output. Assuming entire output is code.")
    return llm_output.strip()
