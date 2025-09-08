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

    Args:
        requirements_content: The content of the dependency file.

    Returns:
        A list of dictionaries, each representing a dependency.
    """
    dependencies = []
    lines = requirements_content.splitlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # This regex handles version specifiers like ==, >=, <, etc.
            match = re.match(r'([a-zA-Z0-9_-]+)\s*([<>=!~]+)\s*([a-zA-Z0-9_.-]+)', line)
            if match:
                name, spec, version = match.groups()
                dependencies.append({"name": name, "version": version, "specifier": spec})
            else:
                # Handle packages without versions
                dependencies.append({"name": line, "version": "any", "specifier": ""})
    return dependencies

def scan_for_vulnerabilities(dependencies: List[Dict[str, str]]) -> str:
    """
    Scans a list of dependencies for known vulnerabilities.

    NOTE: This is a placeholder implementation. A real version would integrate
    with a security database or a tool like `safety` or `snyk`.

    Args:
        dependencies: A list of dependency dictionaries.

    Returns:
        A string report of found vulnerabilities.
    """
    print("Running placeholder vulnerability scan...")
    vulnerabilities = []
    # Simulate finding a vulnerability in an old version of a common library
    for dep in dependencies:
        if dep["name"] == "requests" and dep["version"].startswith("2.2"):
            vulnerabilities.append(
                f"- Package: requests, Version: {dep['version']}, ID: CVE-2023-1234, "
                "Severity: High, Summary: A critical vulnerability was found."
            )

    if not vulnerabilities:
        return "No known vulnerabilities found."

    return "\n".join(vulnerabilities)

def generate_sbom(dependencies: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Generates a Software Bill of Materials (SBOM) in a simplified format.

    NOTE: This is a placeholder. A real implementation would generate a standard
    format like CycloneDX or SPDX.

    Args:
        dependencies: A list of dependency dictionaries.

    Returns:
        A dictionary representing the SBOM.
    """
    print("Generating placeholder SBOM...")
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
        plan = json.loads(llm_output)
        if "optimization_actions" not in plan or not isinstance(plan["optimization_actions"], list):
            raise DependencyError("LLM output is missing 'optimization_actions' list.")
        return plan["optimization_actions"]
    except json.JSONDecodeError:
        raise DependencyError("Failed to decode LLM output as JSON.")
