# core/functor.py
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
from typing import Dict, Any, List

from core.types import SoftwareState, QuantumState

class Functor:
    """
    A class that encapsulates the functorial mapping from software
    systems to quantum systems.
    """
    def __init__(self, beta: float = 0.1, max_features: int = 128):
        self.beta = beta
        self.max_features = max_features

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
        # The existing map_to_density_matrix function expects a dictionary.
        # We convert the pydantic model to a dict to work with it.
        # This assumes that the SoftwareState object will be populated with
        # more than just the fields in the pydantic model, which is an
        # inconsistency in the current codebase.
        state_dict = state.model_dump()

        # The orchestrator also passes metrics, which might be needed to enrich the state
        # for the functor. Let's merge them into the dict.
        if metrics:
            state_dict.update(metrics)

        rho_matrix = map_to_density_matrix(
            state_dict,
            beta=self.beta,
            max_features=self.max_features
        )

        # The QuantumState model expects a list of lists for the density matrix.
        density_matrix_list = rho_matrix.tolist()

        # The state_vector is not computed here, so we leave it as an empty list.
        # This is another inconsistency to be aware of.
        return QuantumState(
            state_vector=[],
            density_matrix=density_matrix_list,
            measurement_basis="computational"
        )


# Placeholder for a more sophisticated feature extractor
def extract_features(state: Dict[str, Any], max_features: int = 128) -> np.ndarray:
    """
    (phi) Extracts a semantic feature vector from a software state.

    NOTE: This is a placeholder. A real implementation would perform deep
    analysis of ASTs, dependency graphs, and other artifacts as described
    in Part 3 of the project plan.

    Args:
        state: The software state to analyze (as a dictionary).
        max_features: The dimension of the feature vector to generate.

    Returns:
        A numpy array representing the feature vector.
    """
    print("Running placeholder feature extraction (phi)...")
    # Simulate features based on simple metrics
    # In a real system, these would be complex, normalized features.
    num_modules = len(state.get("modules", [1]))
    num_dependencies = state.get("dependency_graph", nx.DiGraph()).number_of_edges()

    # Generate a deterministic but pseudo-random vector based on state properties
    seed = hash(f"{num_modules}-{num_dependencies}")
    rng = np.random.default_rng(seed)
    feature_vector = rng.random(size=max_features)

    return feature_vector

def hermitian_assembly(feature_vector: np.ndarray, dep_graph: nx.DiGraph, beta: float = 0.1) -> np.ndarray:
    """
    (Psi) Assembles a Hermitian matrix from a feature vector and dependency graph.

    This function constructs a positive semidefinite (PSD) matrix that encodes
    both the intrinsic properties of the code (from features) and its
    relational structure (from the dependency graph).

    Args:
        feature_vector: The vector from extract_features.
        dep_graph: The dependency graph of the software state.
        beta: A weight for mixing in the graph structure.

    Returns:
        A Hermitian matrix (H).
    """
    print("Running placeholder Hermitian assembly (Psi)...")
    dim = len(feature_vector)

    # 1. Create a PSD matrix from the feature vector (Kernel method)
    # Reshape vector to be a column vector for outer product
    phi = feature_vector.reshape(-1, 1)
    K = phi @ phi.T  # phi * phi^T gives a PSD matrix

    # 2. Mix in graph structure using the normalized Laplacian
    if dep_graph.number_of_nodes() > 0:
        # We need to resize the Laplacian to match the feature dimension
        # This is a simplification. A real implementation would align features and nodes.
        # Use a non-directed view for the Laplacian calculation
        L = nx.normalized_laplacian_matrix(dep_graph.to_undirected()).toarray()

        L_sized = np.zeros((dim, dim))
        size = min(dim, L.shape[0])
        L_sized[:size, :size] = L[:size, :size]

        H = K + beta * L_sized
    else:
        H = K

    # Ensure H is Hermitian (it should be by construction, but this is good practice)
    H = (H + H.T.conj()) / 2

    return H

def create_density_matrix(H: np.ndarray) -> np.ndarray:
    """
    Creates a Gibbs-like density matrix from a Hermitian matrix.

    rho = exp(-H) / Tr(exp(-H))

    Args:
        H: The Hermitian matrix from hermitian_assembly.

    Returns:
        The density matrix (rho).
    """
    # Using scipy's matrix exponential function
    neg_H_exp = expm(-H)
    trace = np.trace(neg_H_exp)

    if trace == 0 or np.isclose(trace, 0):
        # Avoid division by zero; return a maximally mixed state
        dim = H.shape[0]
        return np.identity(dim) / dim

    rho = neg_H_exp / trace
    return rho

def map_to_density_matrix(state: Dict[str, Any], beta: float = 0.1, max_features: int = 128) -> np.ndarray:
    """
    The main functor F that maps a software state to a density matrix.

    This function orchestrates the three-step process:
    1. Feature Extraction (phi)
    2. Hermitian Assembly (Psi)
    3. Density Matrix Creation (Gibbs state)

    Args:
        state: The software state to map (as a dictionary).
        beta: The weight for mixing graph structure into the Hermitian matrix.
        max_features: The dimensionality of the feature space.

    Returns:
        A density matrix representing the quantum state of the software.
    """
    # Step 1: Feature Extraction (phi)
    feature_vector = extract_features(state, max_features=max_features)

    # Step 2: Hermitian Assembly (Psi)
    # The dependency graph is expected to be a networkx graph.
    # If it's not present, an empty graph is created.
    dep_graph_data = state.get("dependency_graph")
    if isinstance(dep_graph_data, nx.DiGraph):
        dep_graph = dep_graph_data
    else:
        # In a real system, we might load this from a serialized format.
        # For the placeholder, we assume it's either a graph or nothing.
        dep_graph = nx.DiGraph()


    H = hermitian_assembly(feature_vector, dep_graph, beta=beta)

    # Step 3: Density Matrix Creation
    rho = create_density_matrix(H)

    return rho
