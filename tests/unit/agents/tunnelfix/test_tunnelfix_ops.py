import pytest
from agents.tunnelfix.ops import parse_optimization_proposal, OptimizationError
from agents.tunnelfix.benchmark import MockBenchmark

def test_parse_optimization_proposal_success():
    llm_output = '{"refactored_code": "a = [i*i for i in range(10)]"}'
    code = parse_optimization_proposal(llm_output)
    assert code == "a = [i*i for i in range(10)]"

def test_parse_optimization_proposal_invalid_json():
    with pytest.raises(OptimizationError, match="Failed to decode"):
        parse_optimization_proposal("not json")

def test_parse_optimization_proposal_missing_key():
    with pytest.raises(OptimizationError, match="missing 'refactored_code' string"):
        parse_optimization_proposal('{"other_key": ""}')

def test_mock_benchmark():
    benchmark = MockBenchmark()
    time = benchmark.run("a = []\nfor i in range(10):\n    a.append(i*i)")
    assert time > 0
