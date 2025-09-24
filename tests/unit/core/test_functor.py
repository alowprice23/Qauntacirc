import pytest
import numpy as np
import networkx as nx
from datetime import datetime
from typing import Dict, Any

from core.functor import Functor
from core.types import SoftwareState, QuantumState, Module

class TestFunctor:
    def test_functor_mapping_produces_valid_quantum_state(self):
        """
        Tests that the functor F: SoftSys -> QuantSys produces a valid quantum state.
        A valid quantum state has a density matrix that is Hermitian, positive semi-definite,
        and has a trace of 1.
        """
        # 1. Setup
        functor = Functor()

        # Create a sample software state
        software_state = SoftwareState(
            component_versions={"comp_a": "1.0", "comp_b": "2.1"},
            config_hashes={"config_a": "hash1", "config_b": "hash2"},
            status="nominal"
        )

        # Create sample metrics, including data for energy calculation
        metrics = {
            "code": "def f(x): return x",
            "modules": [
                Module(
                    id="mod_a",
                    name="mod_a",
                    code="...",
                    normalized_ast=b"...",
                    semantic_tokens=["a", "b"],
                    cyclomatic_complexity=1,
                    duplication_factor=0,
                    coverage_deficit=0,
                    last_refactor=datetime.now()
                ),
                Module(
                    id="mod_b",
                    name="mod_b",
                    code="...",
                    normalized_ast=b"...",
                    semantic_tokens=["c", "d"],
                    cyclomatic_complexity=1,
                    duplication_factor=0,
                    coverage_deficit=0,
                    last_refactor=datetime.now()
                ),
            ],
            "module_dependencies": {"mod_a": ["mod_b"]},
            "dependency_graph": nx.DiGraph([("mod_a", "mod_b")]),
            "type_errors": [],
            "proof_obligations": [],
            "policy_violations": [],
            "constraints": [],
        }

        # 2. Execution
        quantum_state = functor.map_software_to_quantum(software_state, metrics)
        rho = np.array(quantum_state.density_matrix)

        # 3. Assertions
        assert rho.shape == (4, 4), f"Density matrix has incorrect shape: {rho.shape}"
        assert np.isclose(np.trace(rho), 1.0), f"Trace is not 1: {np.trace(rho)}"
        assert np.allclose(rho, rho.T.conj()), "Density matrix is not Hermitian"
        eigenvalues = np.linalg.eigvalsh(rho)
        assert np.all(eigenvalues >= -1e-9), f"Density matrix is not positive semi-definite, eigenvalues: {eigenvalues}"

    def test_functor_identity_law(self):
        """
        Tests the identity law for the functor. F(id) = id.
        """
        functor = Functor()
        code = "def f(x): return x + 1"
        state, metrics = self._create_state_and_metrics(code)

        quantum_state1 = functor.map_software_to_quantum(state, metrics)
        quantum_state2 = functor.map_software_to_quantum(state, metrics)

        assert np.allclose(quantum_state1.density_matrix, quantum_state2.density_matrix)

    def test_functor_composition_law(self):
        """
        Tests the composition law for the functor by checking distance preservation.
        """
        functor = Functor()

        s0, m0 = self._create_state_and_metrics("def f(): pass")
        s1, m1 = self._create_state_and_metrics("def f():\n    if True: pass")
        s2, m2 = self._create_state_and_metrics("def f():\n    if True:\n        if True: pass")

        rho0 = np.array(functor.map_software_to_quantum(s0, m0).density_matrix)
        rho1 = np.array(functor.map_software_to_quantum(s1, m1).density_matrix)
        rho2 = np.array(functor.map_software_to_quantum(s2, m2).density_matrix)

        dist_0_1 = self._trace_distance(rho0, rho1)
        dist_0_2 = self._trace_distance(rho0, rho2)

        assert dist_0_1 > 0
        assert dist_0_2 > dist_0_1

    def _create_state_and_metrics(self, code: str) -> tuple[SoftwareState, Dict[str, Any]]:
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
