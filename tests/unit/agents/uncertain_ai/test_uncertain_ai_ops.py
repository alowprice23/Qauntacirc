import pytest
import json
from agents.uncertain_ai.ops import (
    quantify_uncertainty,
    parse_identified_risks,
    extract_python_code,
    RiskAnalysisError,
)

def test_quantify_uncertainty_heisenberg():
    """
    Tests the Heisenberg-based uncertainty quantification.
    """
    # Case 1: Low complexity, no tests. Should be a low uncertainty.
    low_comp_no_tests = quantify_uncertainty({'cyclomatic_complexity': 1.0}, num_tests=0)
    assert 0 <= low_comp_no_tests <= 1.0

    # Case 2: High complexity, no tests. Should be high uncertainty.
    high_comp_no_tests = quantify_uncertainty({'cyclomatic_complexity': 20.0}, num_tests=0)
    assert high_comp_no_tests > low_comp_no_tests
    assert 0 < high_comp_no_tests <= 1.0

    # Case 3: High complexity, many tests. Uncertainty should decrease.
    high_comp_many_tests = quantify_uncertainty({'cyclomatic_complexity': 20.0}, num_tests=10)
    assert high_comp_many_tests < high_comp_no_tests
    assert 0 <= high_comp_many_tests < 1.0

    # Case 4: More tests should decrease uncertainty.
    uncertainty_one_test = quantify_uncertainty({'cyclomatic_complexity': 10}, num_tests=1)
    uncertainty_ten_tests = quantify_uncertainty({'cyclomatic_complexity': 10}, num_tests=10)
    assert uncertainty_ten_tests < uncertainty_one_test

    # Case 5: More complexity should increase uncertainty.
    uncertainty_low_comp = quantify_uncertainty({'cyclomatic_complexity': 5}, num_tests=5)
    uncertainty_high_comp = quantify_uncertainty({'cyclomatic_complexity': 15}, num_tests=5)
    assert uncertainty_high_comp > uncertainty_low_comp

    # Case 6: Test boundary conditions
    assert quantify_uncertainty({'cyclomatic_complexity': 0}, num_tests=0) >= 0
    assert quantify_uncertainty({'cyclomatic_complexity': 1000}, num_tests=1000) <= 1.0

def test_parse_identified_risks_success():
    llm_output = '{"identified_risks": ["risk1", "risk2"]}'
    risks = parse_identified_risks(llm_output)
    assert risks == ["risk1", "risk2"]

def test_parse_identified_risks_invalid_json():
    with pytest.raises(RiskAnalysisError, match="No valid JSON object found"):
        parse_identified_risks("not json")

def test_parse_identified_risks_missing_key():
    with pytest.raises(RiskAnalysisError, match="No valid JSON object found"):
        parse_identified_risks('{"other_key": []}')

def test_extract_python_code():
    llm_output = "```python\ndef f(): pass\n```"
    code = extract_python_code(llm_output)
    assert code == "def f(): pass"
