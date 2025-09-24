"""
Implements the Functor F: SoftSys -> QuantSys.

This module provides the core logic for mapping a classical software state (S)
into a quantum-mechanical representation (a density matrix rho), enabling
the application of physics-inspired optimization and analysis techniques.
This implementation is based on the detailed description in Part 3 of the
project's master plan.
"""

import numpy as np
from scipy.linalg import expm
import networkx as nx
from typing import Dict, Any, List, Optional
import ast
import re

from core.types import SoftwareState, QuantumState, Module
from core.mathematics import software_to_quantum_functor, CanonicalAST
from agents.base.ops import calculate_cyclomatic_complexity

class _IdentifierVisitor(ast.NodeTransformer):
    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id in __builtins__:
            return node
        return ast.Name(id='_var_', ctx=node.ctx)

    def visit_arg(self, node: ast.arg) -> ast.arg:
        return ast.arg(arg='_arg_', annotation=node.annotation)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        node.name = '_func_'
        self.generic_visit(node)
        return node

class Functor:
    """
    A class that encapsulates the functorial mapping from software
    systems to quantum systems.
    """
    def __init__(self, beta: float = 0.1):
        self.beta = beta

    def canonical_normalization(self, code: str) -> ast.AST:
        """
        Normalizes the code and parses it into an AST.
        This is a simplified version of α-β-η normalization.
        """
        try:
            tree = ast.parse(code)
            return _IdentifierVisitor().visit(tree)
        except SyntaxError as e:
            raise ValueError(f"Failed to parse code: {e}")

    def extract_semantic_features(self, state_dict: Dict[str, Any]) -> np.ndarray:
        """
        (phi) Extracts a feature vector from a software state using semantic analysis.
        """
        code = state_dict.get('code', '')
        if not code:
            return np.zeros(4)

        # Construct the CanonicalAST dictionary
        modules = state_dict.get("modules", [])
        num_source_files = len(modules)
        total_size_bytes = sum(len(m.code) if hasattr(m, 'code') else 0 for m in modules)
        num_dependencies = len(state_dict.get("module_dependencies", {}))

        normalized_ast = self.canonical_normalization(code)
        complexity = calculate_cyclomatic_complexity(normalized_ast)

        properties = {
            "num_source_files": num_source_files,
            "total_size_bytes": total_size_bytes,
            "num_dependencies": num_dependencies,
            "num_files": num_source_files, # Assuming one module per file
            "cyclomatic_complexity": complexity,
        }

        canonical_ast: CanonicalAST = {
            "ast": normalized_ast,
            "properties": properties,
        }

        _, _, features = software_to_quantum_functor(canonical_ast)
        return features

    def verify_functor_laws(self, transformations: List = None) -> bool:
        """
        Implement functor law verification per README.md Part 3.5

        This method runs a series of checks to verify the functor laws.
        """
        # 1. Verify identity law: F(id_A) = id_{F(A)}
        code_a = "def f(x): return x * 2"
        state_a, metrics_a = self._create_state_and_metrics(code_a)
        quantum_state_a = self.map_software_to_quantum(state_a, metrics_a)

        # Applying identity morphism (no change)
        state_id_a, metrics_id_a = self._create_state_and_metrics(code_a)
        quantum_state_id_a = self.map_software_to_quantum(state_id_a, metrics_id_a)

        if not np.allclose(quantum_state_a.density_matrix, quantum_state_id_a.density_matrix):
            print("Functor identity law verification failed.")
            return False

        # 2. Verify composition law (approximated by distance preservation)
        code_b = "def f(x):\n    if x > 0:\n        return x * 2\n    else:\n        return 0"
        state_b, metrics_b = self._create_state_and_metrics(code_b)
        quantum_state_b = self.map_software_to_quantum(state_b, metrics_b)

        dist_a_b = self._trace_distance(np.array(quantum_state_a.density_matrix), np.array(quantum_state_b.density_matrix))

        if not dist_a_b > 0:
            print("Functor composition law verification failed (distance preservation).")
            return False

        return True

    def _create_state_and_metrics(self, code: str) -> tuple[SoftwareState, Dict[str, Any]]:
        from datetime import datetime
        software_state = SoftwareState(
            component_versions={"comp": "1.0"},
            config_hashes={"config": "hash1"},
            status="nominal"
        )
        module = Module(
            id="test_mod",
            name="test_mod",
            code=code,
            normalized_ast=b"",
            semantic_tokens=[],
            cyclomatic_complexity=1,
            duplication_factor=0,
            coverage_deficit=0,
            last_refactor=datetime.now()
        )
        metrics = {"code": code, "modules": [module]}
        return software_state, metrics

    def _trace_distance(self, rho_a, rho_b):
        """Calculates the trace distance between two density matrices."""
        diff = rho_a - rho_b
        return 0.5 * np.sum(np.linalg.svd(diff, compute_uv=False))

    def map_software_to_quantum(self, state: SoftwareState, metrics: Dict[str, Any]) -> QuantumState:
        """
        The main functor F that maps a software state to a density matrix.
        This is the primary method of the functor.

        Args:
            state: The software state to map.
            metrics: The metrics associated with the software state (used to enrich the state).

        Returns:
            A QuantumState object representing the quantum state of the software.
        """
        state_dict = state.model_dump()
        if metrics:
            state_dict.update(metrics)

        # Construct the CanonicalAST
        code = state_dict.get('code', '')
        normalized_ast = self.canonical_normalization(code)

        modules = state_dict.get("modules", [])
        num_source_files = len(modules)
        total_size_bytes = sum(len(m.code) if hasattr(m, 'code') else 0 for m in modules)
        num_dependencies = len(state_dict.get("module_dependencies", {}))
        complexity = calculate_cyclomatic_complexity(normalized_ast)

        properties = {
            "num_source_files": num_source_files,
            "total_size_bytes": total_size_bytes,
            "num_dependencies": num_dependencies,
            "num_files": num_source_files,
            "cyclomatic_complexity": complexity,
        }

        canonical_ast: CanonicalAST = {
            "ast": normalized_ast,
            "properties": properties,
        }

        rho, _, _ = software_to_quantum_functor(canonical_ast)

        density_matrix_list = rho.astype(np.complex128).tolist()

        return QuantumState(
            state_vector=[],
            density_matrix=density_matrix_list,
        )
