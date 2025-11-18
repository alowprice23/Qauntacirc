# agents/uncertain_ai/ops.py
"""
Operations for the UncertainAI Agent.

This module provides utilities for quantifying uncertainty in code, parsing
risk analysis from LLMs, and extracting generated test cases.
"""

import json
import re
from typing import Dict, Any, List

class RiskAnalysisError(Exception):
    """Custom exception for errors during risk analysis."""
    pass

def quantify_uncertainty(metrics: Dict[str, float]) -> float:
    """
    Quantifies the uncertainty of a code artifact based on various metrics.

    NOTE: This is a placeholder implementation. A real version would use
    sophisticated models from a (currently non-existent) `math/uncertainty_bounds.py` file,
    likely involving Bayesian inference or other statistical methods.

    Args:
        metrics: A dictionary of metrics, which could include:
            - 'cyclomatic_complexity'
            - 'llm_confidence' (the confidence score of the generating LLM)
            - 'num_identified_risks'
            - 'test_coverage' (if available)

    Returns:
        A single score from 0.0 (no uncertainty) to 1.0 (maximum uncertainty).
    """
    # Simple weighted formula as a placeholder
    w_complexity = 0.4
    w_confidence = 0.4
    w_risks = 0.2

    complexity = metrics.get('cyclomatic_complexity', 0)
    llm_confidence = metrics.get('llm_confidence', 1.0)
    num_risks = metrics.get('num_identified_risks', 0)

    # Normalize complexity and risks (this is a very rough normalization)
    norm_complexity = min(complexity / 20.0, 1.0) # Assume complexity > 20 is max risk
    norm_risks = min(num_risks / 10.0, 1.0) # Assume > 10 risks is max risk

    # Lower confidence means higher uncertainty
    inv_confidence = 1.0 - llm_confidence

    uncertainty_score = (
        w_complexity * norm_complexity +
        w_confidence * inv_confidence +
        w_risks * norm_risks
    )

    # Clamp the score between 0 and 1
    return max(0.0, min(1.0, uncertainty_score))


def parse_identified_risks(llm_output: str) -> List[str]:
    """
    Parses the JSON output from the risk identification prompt.

    Args:
        llm_output: The raw string output from the LLM.

    Returns:
        A list of strings, where each string is a risk description.

    Raises:
        RiskAnalysisError: If the output cannot be parsed.
    """
    try:
        data = json.loads(llm_output)
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
