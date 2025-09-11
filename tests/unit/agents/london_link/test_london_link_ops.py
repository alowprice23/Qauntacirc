import pytest
from agents.london_link.ops import (
    analyze_dependencies,
    scan_for_vulnerabilities,
    generate_sbom,
    parse_optimization_plan,
    DependencyError,
)

def test_analyze_dependencies():
    content = "requests==2.25.0\n# comment\npydantic>=1.8"
    deps = analyze_dependencies(content)
    assert len(deps) == 2
    assert deps[0]["name"] == "requests"
    assert deps[1]["name"] == "pydantic"

def test_scan_for_vulnerabilities():
    deps = [{"name": "requests", "version": "2.25.0"}]
    report = scan_for_vulnerabilities(deps)
    assert "CVE-2023-1234" in report

    deps_safe = [{"name": "requests", "version": "2.26.0"}]
    report_safe = scan_for_vulnerabilities(deps_safe)
    assert "No known vulnerabilities found" in report_safe

def test_generate_sbom():
    deps = [{"name": "requests", "version": "2.25.0"}]
    sbom = generate_sbom(deps)
    assert sbom["bomFormat"] == "CycloneDX"
    assert len(sbom["components"]) == 1
    assert sbom["components"][0]["name"] == "requests"

def test_parse_optimization_plan_success():
    llm_output = '{"optimization_actions": [{"package": "requests"}]}'
    plan = parse_optimization_plan(llm_output)
    assert len(plan) == 1
    assert plan[0]["package"] == "requests"

def test_parse_optimization_plan_invalid_json():
    with pytest.raises(DependencyError, match="Failed to decode"):
        parse_optimization_plan("not json")

def test_parse_optimization_plan_missing_keys():
    with pytest.raises(DependencyError, match="missing 'optimization_actions' list"):
        parse_optimization_plan('{"other_key": []}')
