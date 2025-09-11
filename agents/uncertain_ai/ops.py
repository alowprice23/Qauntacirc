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

def quantify_uncertainty(metrics: Dict[str, float], num_tests: int) -> float:
    """
    Quantifies the uncertainty of a code artifact using an analogy to the
    Heisenberg Uncertainty Principle (Δx * Δp >= h_bar / 2), where h_bar is
    the reduced Planck constant.

    In this analogy:
    - Δx (uncertainty in "position") represents structural uncertainty,
      proxied by cyclomatic complexity.
    - Δp (uncertainty in "momentum") represents behavioral uncertainty,
      which is inversely related to the number of tests.
    """
    # Δx: Structural uncertainty, modeled using cyclomatic complexity.
    # We use a logarithmic scale to dampen the effect of very high complexity
    # values, preventing them from dominating the score.
    complexity = metrics.get('cyclomatic_complexity', 1.0)
    delta_x = math.log1p(complexity)

    # Δp: Behavioral uncertainty, modeled as being inversely proportional to the
    # number of tests. Adding 1 to num_tests avoids division by zero.
    delta_p = 1.0 / (1.0 + num_tests)

    # The uncertainty score is modeled as the product of the two uncertainties,
    # scaled by a constant factor to keep it within a typical [0, 1] range.
    # This product, Δx * Δp, is our analog for the uncertainty principle.
    scaling_factor = 0.25
    uncertainty_score = scaling_factor * delta_x * delta_p

    # The final score is clamped to the [0, 1] range to ensure it's a
    # well-behaved metric.
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
