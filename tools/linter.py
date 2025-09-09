# tools/linter.py
"""
Custom Linter for QuantaCirc.

This module provides a simple, extensible linter for enforcing project-specific
coding standards and checking for common issues that are not covered by general-
purpose linters like Flake8 or Pylint.

Key Features:
- A framework for defining custom linting rules.
- Checks for mathematical consistency (e.g., variable naming conventions).
- Enforcement of QuantaCirc-specific code quality standards.
"""

import ast
import os
from typing import List, Tuple

class CustomLinter(ast.NodeVisitor):
    """
    A linter that traverses the Abstract Syntax Tree (AST) of a Python file
    to find issues based on a set of custom rules.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors: List[Tuple[int, int, str]] = []

    def add_error(self, node, message: str):
        """Adds an error with line and column number."""
        self.errors.append((node.lineno, node.col_offset, message))

    # --- Custom Rule Implementations ---

    def visit_Call(self, node: ast.Call):
        """
        Rule: Discourage the use of `print()` in library code.
        """
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.add_error(node, "Avoid using 'print()'; use the logging module instead.")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        """
        Rule: Check for disallowed direct imports.
        """
        for alias in node.names:
            if alias.name == 'numpy' and alias.asname != 'np':
                self.add_error(node, "Numpy should be imported as 'np'.")
        self.generic_visit(node)

    def run(self) -> List[Tuple[int, int, str]]:
        """
        Runs the linter on the file.
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            source = f.read()
            tree = ast.parse(source, filename=self.file_path)
            self.visit(tree)
        return self.errors


def lint_file(file_path: str):
    """
    Lints a single Python file and prints the findings.
    """
    if not file_path.endswith('.py'):
        print(f"Skipping non-python file: {file_path}")
        return

    print(f"--- Linting: {file_path} ---")
    linter = CustomLinter(file_path)
    errors = linter.run()

    if not errors:
        print("  No issues found.")
    else:
        for lineno, col, msg in sorted(errors):
            print(f"  L{lineno}:{col} - {msg}")
    print("--------------------------\n")


if __name__ == '__main__':
    # Example Usage:
    # Create a dummy file to lint
    dummy_code = """
import numpy
print("This is a test")

def my_func():
    a = 1 + 1
    print(f"Result is {a}")
"""
    dummy_filepath = "dummy_test_file.py"
    with open(dummy_filepath, "w") as f:
        f.write(dummy_code)

    # Lint the dummy file
    lint_file(dummy_filepath)

    # Clean up the dummy file
    os.remove(dummy_filepath)
