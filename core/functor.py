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

from core.types import SoftwareState, QuantumState
from core.energy_calculator import EnergyCalculator

class Functor:
    """
    A class that encapsulates the functorial mapping from software
    systems to quantum systems.
    """
    def __init__(self, beta: float = 0.1, energy_weights: Optional[Dict[str, float]] = None):
        self.beta = beta
        if energy_weights is None:
            self.energy_weights = {'alpha': 1.0, 'beta': 1.0, 'gamma': 1.0, 'delta': 1.0}
        else:
            self.energy_weights = energy_weights
        self.energy_calculator = EnergyCalculator(**self.energy_weights)

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

        rho_matrix = self._map_to_density_matrix(state_dict)

        # Convert the numpy array of floats to complex numbers before creating the list
        density_matrix_list = rho_matrix.astype(np.complex128).tolist()

        return QuantumState(
            state_vector=[],
            density_matrix=density_matrix_list,
        )

    def _extract_features(self, state_dict: Dict[str, Any]) -> np.ndarray:
        """
        (phi) Extracts a feature vector from a software state using energy components.
        """
        # Create a mock state object for the energy calculator
        mock_state = type('State', (), {})()
        mock_state.code = state_dict.get('code', '')
        mock_state.module_dependencies = state_dict.get('module_dependencies', {})
        mock_state.modules = state_dict.get('modules', [])
        mock_state.type_errors = state_dict.get('type_errors', [])
        mock_state.proof_obligations = state_dict.get('proof_obligations', [])
        mock_state.policy_violations = state_dict.get('policy_violations', [])
        mock_state.dependency_graph = state_dict.get('dependency_graph')
        mock_state.constraints = state_dict.get('constraints', [])
        mock_state.smt_constraints = state_dict.get('smt_constraints', [])
        mock_state.complexity = state_dict.get('complexity', 0)
        mock_state.coupling = state_dict.get('coupling', 0)
        mock_state.debt = state_dict.get('debt', 0)


        _, components = self.energy_calculator.calculate_energy(mock_state)

        feature_vector = np.array([
            components["complexity"],
            components["coupling"],
            components["constraint"],
            components["debt"]
        ])
        return feature_vector

    def _hermitian_assembly(self, feature_vector: np.ndarray, dep_graph: nx.DiGraph) -> np.ndarray:
        """
        (Psi) Assembles a Hermitian matrix from a feature vector and dependency graph.
        """
        dim = len(feature_vector)
        phi = feature_vector.reshape(-1, 1)
        K = phi @ phi.T

        if dep_graph.number_of_nodes() > 0:
            L = nx.normalized_laplacian_matrix(dep_graph.to_undirected()).toarray()
            L_sized = np.zeros((dim, dim))
            size = min(dim, L.shape[0])
            L_sized[:size, :size] = L[:size, :size]
            H = K + self.beta * L_sized
        else:
            H = K

        H = (H + H.T.conj()) / 2
        return H

    def _create_density_matrix(self, H: np.ndarray) -> np.ndarray:
        """
        Creates a Gibbs-like density matrix from a Hermitian matrix.
        """
        neg_H_exp = expm(-H)
        trace = np.trace(neg_H_exp)
        if trace == 0 or np.isclose(trace, 0):
            dim = H.shape[0]
            return np.identity(dim) / dim
        rho = neg_H_exp / trace
        return rho

    def _map_to_density_matrix(self, state_dict: Dict[str, Any]) -> np.ndarray:
        """
        Orchestrates the three-step process to map a software state to a density matrix.
        """
        feature_vector = self._extract_features(state_dict)

        dep_graph_data = state_dict.get("dependency_graph")
        if isinstance(dep_graph_data, nx.DiGraph):
            dep_graph = dep_graph_data
        else:
            dep_graph = nx.DiGraph()

        H = self._hermitian_assembly(feature_vector, dep_graph)
        rho = self._create_density_matrix(H)
        return rho
