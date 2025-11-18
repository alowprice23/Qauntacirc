# agents/schrodinger_dev/ops.py
"""
Operations for the SchrodingerDev Agent.

This module provides utilities for handling template-driven code generation,
parsing code from LLM outputs, and performing basic validation on the
generated code skeletons.
"""

import re
import ast
from typing import Dict, Any, Optional

# In a real implementation, this would interact with a more robust
# template management system that loads templates from the `templates/` dir.
_TEMPLATE_CACHE: Dict[str, str] = {
    "default_function": "def {function_name}():\n    ...",
    "default_class": "class {class_name}:\n    def __init__(self):\n        ...\n"
}

class CodeGenerationError(Exception):
    """Custom exception for errors during code generation or parsing."""
    pass

def load_code_template(template_name: str) -> Optional[str]:
    """
    Loads a code template by name.

    NOTE: This is a placeholder implementation. A real version would load
    from the `templates/` directory on the filesystem.

    Args:
        template_name: The name of the template to load.

    Returns:
        The template content as a string, or None if not found.
    """
    print(f"Attempting to load placeholder template: {template_name}")
    return _TEMPLATE_CACHE.get(template_name)

def extract_python_code(llm_output: str) -> str:
    """
    Extracts a Python code block from the LLM's markdown-formatted output.

    Args:
        llm_output: The raw string output from the LLM.

    Returns:
        The extracted Python code.

    Raises:
        CodeGenerationError: If a Python code block cannot be found.
    """
    # Regex to find a python markdown block
    match = re.search(r"```python\n(.*?)```", llm_output, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback for a simple code block
    match = re.search(r"```\n(.*?)```", llm_output, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If no markdown block is found, assume the whole output is code,
    # but log a warning.
    print("Warning: No markdown block found in LLM output. Assuming entire output is code.")
    return llm_output.strip()


def validate_python_syntax(code: str) -> None:
    """
    Validates that the given string is syntactically correct Python code.

    Args:
        code: The Python code string to validate.

    Raises:
        CodeGenerationError: If the code has a syntax error.
    """
    try:
        ast.parse(code)
    except SyntaxError as e:
        raise CodeGenerationError(f"Generated code has a syntax error: {e}")

def create_code_and_proof_files(code_skeleton: str, proof_skeleton: str, task_id: str) -> Dict[str, str]:
    """
    Creates a mapping of file paths to content for the generated code and proof.

    Args:
        code_skeleton: The generated Python code for the implementation.
        proof_skeleton: The generated Python code for the tests.
        task_id: The ID of the task, used for naming files.

    Returns:
        A dictionary mapping proposed file paths to their content.
    """
    # A real implementation might have a more sophisticated file naming strategy.
    file_map = {
        f"src/generated/{task_id.lower()}_code.py": code_skeleton,
        f"tests/generated/test_{task_id.lower()}_code.py": proof_skeleton,
    }
    return file_map
