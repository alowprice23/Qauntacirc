# agents/phonon_flow/ops.py
"""
Operations for the PhononFlow Agent.

This module provides utilities for analyzing code structure, building
dependency graphs, and calculating the "speed of sound" in the codebase,
which is a measure of its maintainability and ease of change propagation.
"""

import ast
import json
import math
from typing import Dict, List, Tuple, Any

from core.dependency_graph import DependencyGraph
from agents.base import ops as base_ops

class PhononFlowError(Exception):
    """Custom exception for errors during phonon flow analysis."""
    pass

class ImportVisitor(ast.NodeVisitor):
    """
    An AST visitor to find all imported modules in a file.
    It expects fully qualified imports (e.g., 'import src.utils').
    """
    def __init__(self):
        self.imports = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

def build_dependency_graph(file_map: Dict[str, str]) -> DependencyGraph:
    """Builds a DependencyGraph from a map of file paths to source code."""
    dependencies: List[Tuple[str, str]] = []

    path_to_module = {path: path.replace('/', '.').replace('.py', '') for path in file_map}
    all_modules = set(path_to_module.values())

    for file_path, code in file_map.items():
        try:
            tree = ast.parse(code)
            visitor = ImportVisitor()
            visitor.visit(tree)

            current_module = path_to_module[file_path]

            for imp in visitor.imports:
                # The resolver now expects a direct match in all_modules
                if imp in all_modules:
                    if current_module != imp:
                        dependencies.append((current_module, imp))
        except SyntaxError:
            continue

    return DependencyGraph(list(all_modules), dependencies)

def calculate_complexity_density(code: str) -> float:
    """Calculates complexity per line of code."""
    lines = code.count('\n') + 1
    if lines == 0:
        return 0.0
    try:
        ast_tree = base_ops.parse_to_ast(code)
        complexity = base_ops.calculate_cyclomatic_complexity(ast_tree)
        return complexity / lines
    except Exception:
        return 10.0 # Default to a high density on parsing error

def calculate_speed_of_sound(coupling: float, density: float) -> float:
    """
    Calculates the "speed of sound" in the code, a measure of its quality.
    v_s = sqrt( (1/Coupling) / Density )
    Higher speed is better, resulting from low coupling and low density.
    """
    if coupling <= 0 or density <= 0:
        return 0.0

    # The "stiffness" is inversely proportional to coupling
    stiffness = 1.0 / coupling

    # Speed of sound is sqrt(stiffness / density)
    speed = math.sqrt(stiffness / density)
    return speed

def parse_refactoring_proposal(llm_output: str) -> Dict[str, str]:
    """Parses the JSON output from the refactoring prompt."""
    try:
        data = json.loads(llm_output)
        if "refactored_code" not in data or "explanation" not in data:
            raise PhononFlowError("LLM output is missing required keys.")
        return data
    except json.JSONDecodeError:
        raise PhononFlowError("Failed to decode LLM output as JSON.")
