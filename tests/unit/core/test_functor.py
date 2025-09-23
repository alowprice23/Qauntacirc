import pytest
import numpy as np
import networkx as nx
from datetime import datetime

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
        # Check shape (4x4 because of 4 energy components)
        assert rho.shape == (4, 4), f"Density matrix has incorrect shape: {rho.shape}"

        # Check for trace of 1
        assert np.isclose(np.trace(rho), 1.0), f"Trace is not 1: {np.trace(rho)}"

        # Check for Hermitian property (rho == rho_dagger)
        assert np.allclose(rho, rho.T.conj()), "Density matrix is not Hermitian"

        # Check for positive semi-definite property (all eigenvalues >= 0)
        eigenvalues = np.linalg.eigvalsh(rho)
        assert np.all(eigenvalues >= -1e-9), f"Density matrix is not positive semi-definite, eigenvalues: {eigenvalues}"

    def test_functor_identity_law(self):
        """
        Tests the identity law for the functor. F(id) = id.
        This is tested by ensuring that two identical software states map to the
        same quantum state.
        """
        # 1. Setup
        functor = Functor()

        software_state1 = SoftwareState(
            component_versions={"comp": "1.0"},
            config_hashes={"config": "hash1"},
            status="nominal"
        )
        module = Module(
            name="a",
            code="pass",
            normalized_ast=b"pass",
            semantic_tokens=["pass"],
            cyclomatic_complexity=1,
            duplication_factor=0,
            coverage_deficit=0,
            last_refactor=datetime.now()
        )
        metrics1 = {"code": "pass", "modules": [module], "module_dependencies": {}, "dependency_graph": None, "constraints": []}

        software_state2 = SoftwareState(
            component_versions={"comp": "1.0"},
            config_hashes={"config": "hash1"},
            status="nominal"
        )
        metrics2 = {"code": "pass", "modules": [module], "module_dependencies": {}, "dependency_graph": None, "constraints": []}

        # 2. Execution
        quantum_state1 = functor.map_software_to_quantum(software_state1, metrics1)
        rho1 = np.array(quantum_state1.density_matrix)

        quantum_state2 = functor.map_software_to_quantum(software_state2, metrics2)
        rho2 = np.array(quantum_state2.density_matrix)

        # 3. Assertion
        assert np.allclose(rho1, rho2), "Identical software states should map to identical quantum states"

    def test_functor_composition_law(self):
        """
        Tests the composition law for the functor. F(g . f) = F(g) . F(f).
        This is a more abstract property. We can approximate it by checking if the
        functor preserves some notion of distance or similarity.
        A larger change in the software state should result in a larger distance
        between the corresponding quantum states.
        """
        # 1. Setup
        functor = Functor()

        def create_state_and_metrics(complexity: float):
            software_state = SoftwareState(
                component_versions={"comp": "1.0"},
                config_hashes={"config": "hash1"},
                status="nominal"
            )
            module = Module(
                name="a",
                code="pass",
                normalized_ast=b"pass",
                semantic_tokens=["pass"],
                cyclomatic_complexity=complexity,
                duplication_factor=0,
                coverage_deficit=0,
                last_refactor=datetime.now()
            )
            metrics = {"code": "pass", "modules": [module], "module_dependencies": {}, "dependency_graph": None, "constraints": []}
            return software_state, metrics

        s0, m0 = create_state_and_metrics(1.0)
        s1, m1 = create_state_and_metrics(2.0)  # Small change
        s2, m2 = create_state_and_metrics(10.0) # Large change

        # 2. Execution
        rho0 = np.array(functor.map_software_to_quantum(s0, m0).density_matrix)
        rho1 = np.array(functor.map_software_to_quantum(s1, m1).density_matrix)
        rho2 = np.array(functor.map_software_to_quantum(s2, m2).density_matrix)

        def trace_distance(rho_a, rho_b):
            """Calculates the trace distance between two density matrices."""
            diff = rho_a - rho_b
            # Eigenvalues of a Hermitian matrix are real.
            # sqrtm can be computationally expensive. Use eigenvalues instead.
            # The trace distance is 0.5 * Tr(|A|), where |A| = sqrt(A*A).
            # The trace of |A| is the sum of the singular values of A.
            return 0.5 * np.sum(np.linalg.svd(diff, compute_uv=False))

        dist_0_1 = trace_distance(rho0, rho1)
        dist_0_2 = trace_distance(rho0, rho2)

        # 3. Assertion
        # A larger change in software state (complexity 1->10) should result in a
        # larger trace distance than a smaller change (complexity 1->2).
        assert dist_0_1 > 0, "Identical states should have non-zero distance for different complexities"
        assert dist_0_2 > dist_0_1, "Functor should preserve distance ordering"
