import pytest
from agents.phonon_flow.ops import analyze_data_flow, parse_optimization_plan, DataFlowError

def test_analyze_data_flow_with_request():
    file_map = {"src/a.py": "import requests\nrequests.get('http://example.com')"}
    description = analyze_data_flow(file_map)
    assert "synchronous HTTP request" in description

def test_analyze_data_flow_no_request():
    file_map = {"src/a.py": "print('hello')"}
    description = analyze_data_flow(file_map)
    assert "No clear inter-component data flow patterns" in description

def test_parse_optimization_plan_success():
    llm_output = '{"analysis": "a", "proposed_pattern": "p", "implementation_plan": [], "expected_outcome": "o"}'
    plan = parse_optimization_plan(llm_output)
    assert "analysis" in plan

def test_parse_optimization_plan_invalid_json():
    with pytest.raises(DataFlowError, match="Failed to decode"):
        parse_optimization_plan("not json")

def test_parse_optimization_plan_missing_keys():
    with pytest.raises(DataFlowError, match="missing required keys"):
        parse_optimization_plan('{"analysis": ""}')
