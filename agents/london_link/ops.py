# agents/london_link/ops.py
"""
Operations for the LondonLink Agent.

This module provides utilities for parsing dependency files, simulating
vulnerability scans, generating SBOMs, and parsing optimization plans.
"""

import json
import re
from typing import Dict, List, Any

class DependencyError(Exception):
    """Custom exception for errors during dependency analysis."""
    pass

def analyze_dependencies(requirements_content: str) -> List[Dict[str, str]]:
    """
    Parses a requirements.txt-style file content into a structured list.
    """
    dependencies = []
    lines = requirements_content.splitlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            match = re.match(r'([a-zA-Z0-9_-]+)\s*([<>=!~]+)\s*([a-zA-Z0-9_.-]+)', line)
            if match:
                name, spec, version = match.groups()
                dependencies.append({"name": name, "version": version, "specifier": spec})
            else:
                dependencies.append({"name": line, "version": "any", "specifier": ""})
    return dependencies

_VULNERABILITY_DB = {
    "requests": {
        "2.25.0": {"id": "CVE-2023-1234", "severity": "High", "summary": "Request smuggling vulnerability"},
    }
}

def scan_for_vulnerabilities(dependencies: List[Dict[str, str]]) -> str:
    """
    Scans a list of dependencies for known vulnerabilities.
    """
    vulnerabilities = []
    for dep in dependencies:
        if dep["name"] in _VULNERABILITY_DB:
            for version, vuln in _VULNERABILITY_DB[dep["name"]].items():
                if dep["version"] == version:
                    vulnerabilities.append(
                        f"- Package: {dep['name']}, Version: {dep['version']}, ID: {vuln['id']}, "
                        f"Severity: {vuln['severity']}, Summary: {vuln['summary']}"
                    )

    if not vulnerabilities:
        return "No known vulnerabilities found."

    return "\n".join(vulnerabilities)

def generate_sbom(dependencies: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Generates a Software Bill of Materials (SBOM) in a simplified format.
    """
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "components": [
            {"type": "library", "name": d["name"], "version": d["version"]}
            for d in dependencies
        ]
    }

def parse_optimization_plan(llm_output: str) -> List[Dict[str, str]]:
    """
    Parses the JSON output from the LLM into a list of optimization actions.
    """
    try:
        data = json.loads(llm_output)
        if "optimization_actions" not in data or not isinstance(data["optimization_actions"], list):
            raise DependencyError("LLM output is missing 'optimization_actions' list.")
        return data["optimization_actions"]
    except json.JSONDecodeError:
        raise DependencyError("Failed to decode LLM output as JSON.")
