import pytest
from agents.london_link.ops import (
    build_dependency_graph,
    calculate_attraction_potential,
    parse_refactoring_proposal,
    LondonLinkError,
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
    assert graph.graph.has_edge("src.main", "src.utils")
    assert graph.graph.has_edge("src.main", "src.services.api")
    assert graph.graph.has_edge("src.services.api", "src.utils")

def test_calculate_attraction_potential():
    # High distance -> low attraction
    low_attraction = calculate_attraction_potential(r=10, c6=100)
    # Low distance -> high attraction
    high_attraction = calculate_attraction_potential(r=2, c6=100)
    assert low_attraction > high_attraction # Potential is negative
    assert calculate_attraction_potential(r=1, c6=100) == -100.0

def test_parse_refactoring_proposal_success():
    llm_output = '{"refactored_code": "new code", "explanation": "because", "refactored_module_path": "src/a.py"}'
    proposal = parse_refactoring_proposal(llm_output)
    assert proposal["refactored_code"] == "new code"
    assert proposal["explanation"] == "because"

def test_parse_refactoring_proposal_invalid_json():
    with pytest.raises(LondonLinkError, match="Failed to decode"):
        parse_refactoring_proposal("not json")

def test_parse_refactoring_proposal_missing_keys():
    with pytest.raises(LondonLinkError, match="missing required keys"):
        parse_refactoring_proposal('{"refactored_code": ""}')
