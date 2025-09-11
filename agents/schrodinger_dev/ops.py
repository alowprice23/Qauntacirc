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
import os

class CodeGenerationError(Exception):
    """Custom exception for errors during code generation or parsing."""
    pass

def load_code_template(template_name: str) -> Optional[str]:
    """
    Loads a code template by name from the templates directory.

    Args:
        template_name: The name of the template to load.

    Returns:
        The template content as a string, or None if not found.
    """
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    template_file = os.path.join(template_dir, f"{template_name}.py.template")

    if not os.path.exists(template_file):
        return None

    with open(template_file, "r") as f:
        return f.read()

def extract_multiple_python_code(llm_output: str) -> list[str]:
    """
    Extracts multiple Python code blocks from the LLM's markdown-formatted output.

    Args:
        llm_output: The raw string output from the LLM.

    Returns:
        A list of extracted Python code strings.
    """
    # Regex to find all python markdown blocks
    pattern = re.compile(r"```python\n(.*?)```", re.DOTALL)
    matches = pattern.findall(llm_output)
    if matches:
        return [match.strip() for match in matches]

    # Fallback for simple code blocks
    pattern = re.compile(r"```\n(.*?)```", re.DOTALL)
    matches = pattern.findall(llm_output)
    if matches:
        return [match.strip() for match in matches]

    return []


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
        proof_skeleton: The generated Python code for the formal proof.
        task_id: The ID of the task, used for naming files.

    Returns:
        A dictionary mapping proposed file paths to their content.
    """
    # A real implementation might have a more sophisticated file naming strategy.
    file_map = {
        f"src/generated/{task_id.lower()}_code.py": code_skeleton,
        f"proofs/generated/prove_{task_id.lower()}_code.py": proof_skeleton,
    }
    return file_map
