# tools/validator.py
"""
Validation utilities for QuantaCirc.

This module provides a centralized place for various validation tasks, ensuring
the integrity and quality of the system's configuration, data, and code.

Key Features:
- Configuration validation against predefined schemas.
- Mathematical property validation for simulation results.
- Code quality checks to enforce project standards.
"""

import jsonschema
from typing import Dict, Any, List
import numpy as np
import ast

# Assuming access to math_utils for property validation
# from math_utils.verification_utils import check_invariants
from core.types import QCState, AgentConfig

class Validator:
    """
    A generic validator for various system components.
    """
    def __init__(self):
        """Initializes the Validator."""
        pass

    def validate_config(self, config_data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """
        Validates a configuration dictionary against a JSON schema.

        Args:
            config_data (Dict[str, Any]): The configuration data to validate.
            schema (Dict[str, Any]): The JSON schema.

        Returns:
            List[str]: A list of validation errors. Empty if valid.
        """
        try:
            jsonschema.validate(instance=config_data, schema=schema)
            return []
        except jsonschema.exceptions.ValidationError as e:
            return [str(e)]
        except jsonschema.exceptions.SchemaError as e:
            return [f"Invalid schema: {e}"]

    def validate_quantum_state_properties(self, state: QCState) -> List[str]:
        """
        Validates mathematical properties of a quantum state.

        Checks for:
        - Normalization of the state vector.
        - Hermiticity and trace of the density matrix.

        Args:
            state (QCState): The QuantaCirc state containing the quantum information.

        Returns:
            List[str]: A list of property violations.
        """
        errors = []
        if not state.quantum_state:
            return ["No quantum state to validate."]

        q_state = state.quantum_state

        # 1. Validate state vector normalization
        if q_state.state_vector:
            norm_sq = np.sum(np.abs(np.array(q_state.state_vector))**2)
            if not np.isclose(norm_sq, 1.0):
                errors.append(f"State vector is not normalized. Sum of squared magnitudes is {norm_sq}.")

        # 2. Validate density matrix properties
        if q_state.density_matrix:
            dm = np.array(q_state.density_matrix)
            # Check if it's a square matrix
            if dm.ndim != 2 or dm.shape[0] != dm.shape[1]:
                errors.append("Density matrix is not a square matrix.")
            else:
                # Check for Hermiticity
                if not np.allclose(dm, dm.T.conj()):
                    errors.append("Density matrix is not Hermitian.")
                # Check if trace is 1
                if not np.isclose(np.trace(dm), 1.0):
                    errors.append(f"Density matrix trace is not 1. Found: {np.trace(dm)}")

        # Example of using a mock check_invariants from math_utils
        # if not check_invariants(state.quantum_state.dict()):
        #     errors.append("Mathematical invariant violated in simulation result.")

        return errors

    def check_code_quality(self, file_path: str) -> List[str]:
        """
        Performs basic code quality checks on a given file.
        This is a simplified stand-in for a real linter.

        Args:
            file_path (str): The path to the Python file to check.

        Returns:
            List[str]: A list of quality issues found.
        """
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError) as e:
            return [f"Could not read file {file_path}: {e}"]

        # Check for line length and tabs
        for i, line in enumerate(content.splitlines(), 1):
            if len(line) > 120:
                issues.append(f"Line {i} exceeds 120 characters.")
            if '\t' in line:
                issues.append(f"Tab character found on line {i}.")

        # Check for missing function docstrings using AST
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        issues.append(f"Function '{node.name}' on line {node.lineno} is missing a docstring.")
        except SyntaxError as e:
            issues.append(f"Could not parse file {file_path} for docstring check: {e}")

        return issues


if __name__ == '__main__':
    # Example Usage
    print("Validator Tool")
    validator = Validator()

    # 1. Schema Validation Example
    schema = {"type": "object", "properties": {"name": {"type": "string"}, "value": {"type": "number"}}}
    valid_config = {"name": "test", "value": 123}
    invalid_config = {"name": "test", "value": "abc"}

    print(f"Validating good config: {validator.validate_config(valid_config, schema)}")
    print(f"Validating bad config: {validator.validate_config(invalid_config, schema)}")

    # 2. Code Quality Example (on this file itself)
    quality_issues = validator.check_code_quality(__file__)
    print(f"Code quality issues in this file: {quality_issues}")

    # 3. Quantum State Validation Example
    from core.types import QuantumState
    valid_q_state = QCState(
        software_state={"component_versions": {}, "config_hashes": {}, "status": "nominal"},
        quantum_state=QuantumState(
            state_vector=[complex(1/np.sqrt(2)), complex(1/np.sqrt(2))],
            density_matrix=[[complex(0.5), complex(0)], [complex(0), complex(0.5)]]
        ),
        energy=1.0, energy_components={"static":1, "dynamic":0, "interaction":0},
        lyapunov_potential=0.1, contraction_factor=0.9
    )
    invalid_q_state = QCState(
        software_state={"component_versions": {}, "config_hashes": {}, "status": "nominal"},
        quantum_state=QuantumState(
            state_vector=[complex(1), complex(1)], # Not normalized
            density_matrix=[[complex(1), complex(1)], [complex(0), complex(0)]] # Not Hermitian, trace is not 1
        ),
        energy=1.0, energy_components={"static":1, "dynamic":0, "interaction":0},
        lyapunov_potential=0.1, contraction_factor=0.9
    )
    print(f"\nValidating good quantum state: {validator.validate_quantum_state_properties(valid_q_state)}")
    print(f"Validating bad quantum state: {validator.validate_quantum_state_properties(invalid_q_state)}")
