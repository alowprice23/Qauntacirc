import pytest
from agents.phonon_flow.ops import (
    build_dependency_graph,
    calculate_complexity_density,
    calculate_speed_of_sound,
    parse_refactoring_proposal,
    PhononFlowError,
)

def test_build_dependency_graph():
    file_map = {
        "src/main.py": "import src.utils\nimport src.services.api",
        "src/utils.py": "import os",
        "src/services/api.py": "import src.utils"
    }
    graph = build_dependency_graph(file_map)

    assert "src.main" in graph.graph
    assert "src.utils" in graph.graph
    assert "src.services.api" in graph.graph

    # Corrected assertions based on how the simple parser works
    assert graph.graph.has_edge("src.main", "src.utils")
    assert graph.graph.has_edge("src.main", "src.services.api")
    assert graph.graph.has_edge("src.services.api", "src.utils")

def test_calculate_complexity_density():
    # Simple code, complexity 1, 2 lines -> 0.5
    code = "def f():\n  return 1"
    density = calculate_complexity_density(code)
    assert density == pytest.approx(0.5)

    # More complex code
    complex_code = "def f(x):\n  if x > 0:\n    return 1\n  else:\n    return 0"
    density = calculate_complexity_density(complex_code)
    # Complexity is 2, lines is 5 -> 0.4
    assert density == pytest.approx(0.4)

def test_calculate_speed_of_sound():
    # High coupling, high density -> low speed
    low_speed = calculate_speed_of_sound(coupling=10, density=5)

    # Low coupling, low density -> high speed
    high_speed = calculate_speed_of_sound(coupling=2, density=1)

    assert high_speed > low_speed
    assert calculate_speed_of_sound(coupling=0, density=1) == 0

def test_parse_refactoring_proposal_success():
    llm_output = '{"refactored_code": "new code", "explanation": "because"}'
    proposal = parse_refactoring_proposal(llm_output)
    assert proposal["refactored_code"] == "new code"
    assert proposal["explanation"] == "because"

def test_parse_refactoring_proposal_invalid_json():
    with pytest.raises(PhononFlowError, match="Failed to decode"):
        parse_refactoring_proposal("not json")

def test_parse_refactoring_proposal_missing_keys():
    with pytest.raises(PhononFlowError, match="missing required keys"):
        parse_refactoring_proposal('{"refactored_code": ""}')
