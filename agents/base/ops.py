# agents/base/ops.py
"""
A shared operations library for code analysis tasks, such as AST parsing,
complexity analysis, and feature extraction.
"""

import ast
import inspect
from typing import List, Union, Dict, Any


def parse_to_ast(source_code: str) -> ast.Module:
    """
    Parses a string containing Python source code into an AST.

    Args:
        source_code: The Python code to parse.

    Returns:
        An ast.Module node representing the parsed code.
    """
    try:
        return ast.parse(source_code)
    except SyntaxError as e:
        print(f"Error parsing source code: {e}")
        raise


def get_function_definitions(tree: ast.Module) -> List[ast.FunctionDef]:
    """
    Extracts all top-level function definitions from an AST.

    Args:
        tree: The AST to search.

    Returns:
        A list of ast.FunctionDef nodes.
    """
    return [node for node in tree.body if isinstance(node, ast.FunctionDef)]


def get_class_definitions(tree: ast.Module) -> List[ast.ClassDef]:
    """
    Extracts all top-level class definitions from an AST.

    Args:
        tree: The AST to search.

    Returns:
        A list of ast.ClassDef nodes.
    """
    return [node for node in tree.body if isinstance(node, ast.ClassDef)]


def calculate_cyclomatic_complexity(node: Union[ast.FunctionDef, ast.ClassDef, ast.Module]) -> int:
    """
    Calculates the cyclomatic complexity of a function, class, or module.
    Complexity = Edges - Nodes + 2P
    In a control flow graph, this simplifies to 1 + (number of decision points).
    """
    complexity = 1
    decision_points = (
        ast.If, ast.For, ast.While, ast.And, ast.Or,
        ast.withitem, ast.ExceptHandler, ast.AsyncFor, ast.AsyncWith
    )

    for child in ast.walk(node):
        if isinstance(child, decision_points):
            complexity += 1
        # `elif` is just another `if` in the `orelse` block, so it's counted
        if isinstance(child, ast.If) and child.orelse:
             # This is a simplification; doesn't correctly handle all `elif` chains
             pass

    return complexity


def detect_duplicate_code(source_files: Dict[str, str], min_lines: int = 5) -> List[Dict[str, Any]]:
    """
    A placeholder for a duplicate code detection implementation.
    A real implementation would use more sophisticated algorithms like Rabin-Karp
    or suffix trees to find duplicated blocks of code.

    Args:
        source_files: A dictionary mapping file paths to their content.
        min_lines: The minimum number of lines to consider a duplicate.

    Returns:
        A list of dictionaries, each describing a detected duplicate.
    """
    print("Placeholder for duplicate code detection.")
    # In a real implementation, you would:
    # 1. Normalize and hash lines/blocks of code.
    # 2. Compare hashes across all files to find matches.
    # 3. Report matches with file paths and line numbers.
    return []


def get_docstring(node: Union[ast.FunctionDef, ast.ClassDef, ast.Module]) -> str:
    """
    Extracts the docstring from a node, if it exists.
    """
    return ast.get_docstring(node)
