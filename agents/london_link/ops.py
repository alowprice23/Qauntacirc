import ast
import json
import math
import networkx as nx
from typing import Dict, List, Tuple, Any

from core.dependency_graph import DependencyGraph
from agents.base import ops as base_ops

class LondonLinkError(Exception):
    pass

# Copied from PhononFlow - in a real system, this would be in a shared location.
class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name)
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.add(node.module)

def build_dependency_graph(file_map: Dict[str, str]) -> DependencyGraph:
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
                if imp in all_modules:
                    if current_module != imp:
                        dependencies.append((current_module, imp))
        except SyntaxError:
            continue
    return DependencyGraph(list(all_modules), dependencies)

def calculate_attraction_potential(r, c6):
    """
    Calculates the London dispersion force potential V(r) = -C6 / r^6.
    """
    if r == 0:
        return -float('inf') # Infinite attraction at zero distance
    return -c6 / (r**6)

def parse_refactoring_proposal(llm_output: str) -> Dict[str, str]:
    """Parses the JSON output from the refactoring prompt."""
    try:
        data = json.loads(llm_output)
        if "refactored_code" not in data or "explanation" not in data:
            raise LondonLinkError("LLM output is missing required keys.")
        return data
    except json.JSONDecodeError:
        raise LondonLinkError("Failed to decode LLM output as JSON.")
