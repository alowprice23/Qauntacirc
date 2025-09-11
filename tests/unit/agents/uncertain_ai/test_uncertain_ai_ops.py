import pytest
import json
from agents.uncertain_ai.ops import (
    calculate_risk_bound,
    quantify_uncertainty,
    parse_identified_risks,
    extract_python_code,
    RiskAnalysisError,
)

def test_calculate_risk_bound():
    assert calculate_risk_bound(0) == 1.0
    assert calculate_risk_bound(10) < 1.0
    assert calculate_risk_bound(100) < calculate_risk_bound(10)

def test_quantify_uncertainty():
    metrics = {'cyclomatic_complexity': 10, 'llm_confidence': 0.8}
    uncertainty = quantify_uncertainty(metrics, num_tests=100)
    assert 0 <= uncertainty <= 1.0

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
