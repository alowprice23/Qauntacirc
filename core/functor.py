# core/functor.py
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
=======
>>>>>>> remotes/origin/feat/core-infrastructure

"""
Implements the functor for mapping classical software systems to quantum states.

This module is the bridge between the classical representation of a software
system and its quantum-mechanical counterpart. The functor defines the rules
for this transformation.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Any, List

from core.types import SoftwareState, QuantumState, QCState
from core.energy_calculator import EnergyCalculator

# Constants for quantum state mapping
DEFAULT_HILBERT_SPACE_DIM = 256  # Dimension of the Hilbert space for the quantum state

class Functor:
    """
    A functor that maps a classical software system state to a quantum state.

    The mapping is based on various metrics of the software system, such as
    code complexity, runtime performance, and dependency structure. These metrics
    are used to construct a corresponding quantum state, typically represented
    by a state vector or a density matrix.
    """

    def __init__(self, energy_calculator: EnergyCalculator,
                 hilbert_space_dim: int = DEFAULT_HILBERT_SPACE_DIM):
        """
        Initializes the Functor.

        Args:
            energy_calculator: An instance of EnergyCalculator to compute energy,
                               which influences the quantum state representation.
            hilbert_space_dim: The dimension of the Hilbert space for the quantum states.
        """
        self.energy_calculator = energy_calculator
        self.hilbert_space_dim = hilbert_space_dim

    def map_software_to_quantum(self, software_state: SoftwareState,
                                metrics: Dict[str, Any]) -> QuantumState:
        """
        Maps a classical software state to a quantum state.

        This is the core function of the functor. It takes the classical state
        and associated metrics and generates a quantum state vector. The properties
        of this vector (e.g., its entanglement, coherence) are determined by the
        software's characteristics.

        Args:
            software_state: The classical state of the software.
            metrics: A dictionary of metrics associated with the software state.
                     This should include static, dynamic, and interaction metrics.

        Returns:
            A QuantumState object representing the software system.
        """
        # 1. Compute energy components from metrics
        static_metrics = metrics.get('static', {})
        dynamic_metrics = metrics.get('dynamic', {})
        interaction_metrics = metrics.get('interaction', {})

        e_static = self.energy_calculator.compute_static_energy(static_metrics)
        e_dynamic = self.energy_calculator.compute_dynamic_energy(dynamic_metrics)
        e_interaction = self.energy_calculator.compute_interaction_energy(interaction_metrics)

        # 2. Generate a quantum state vector based on energy components.
        # This is a simplified, heuristic-based mapping. A more sophisticated
        # model would involve a more principled transformation.

        # Use energy components to define properties of the quantum state.
        # For example, higher energy might correspond to a more mixed or chaotic state.

        # Create a base state (e.g., a uniform superposition)
        base_vector = np.ones(self.hilbert_space_dim, dtype=complex) / np.sqrt(self.hilbert_space_dim)

        # Perturb the state based on energy components.
        # Let's create a phase profile based on the energies.
        # We can map each energy component to a frequency in the phase.

        phases = np.zeros(self.hilbert_space_dim)
        indices = np.arange(self.hilbert_space_dim)

        # Static energy could influence the low-frequency components of the phase
        phases += e_static * np.sin(2 * np.pi * indices / self.hilbert_space_dim)

        # Dynamic energy could influence higher-frequency components
        phases += e_dynamic * np.sin(4 * np.pi * indices / self.hilbert_space_dim)

        # Interaction energy could introduce complex, non-local correlations (entanglement)
        # This is harder to model simply. As a proxy, let's add a quadratic phase term.
        phases += e_interaction * np.sin(2 * np.pi * (indices**2) / (self.hilbert_space_dim**2))

        # Apply the phases to the base vector
        state_vector = base_vector * np.exp(1j * phases)

        # Ensure normalization
        state_vector /= np.linalg.norm(state_vector)

        return QuantumState(
            state_vector=state_vector.tolist(),
            measurement_basis="computational"
        )

    def compute_density_matrix(self, quantum_state: QuantumState) -> List[List[complex]]:
        """
        Computes the density matrix for a given quantum state.

        If the state is pure (represented by a state vector), the density matrix is
        rho = |psi><psi|. If the state is mixed, this would be more complex.

        Args:
            quantum_state: The QuantumState object.

        Returns:
            The computed density matrix as a 2D list of complex numbers.
        """
        if quantum_state.density_matrix:
            return quantum_state.density_matrix

        state_vector = np.array(quantum_state.state_vector, dtype=complex)

        # Ensure it's a column vector for the outer product
        psi = state_vector.reshape(-1, 1)

        density_matrix = psi @ psi.conj().T

        return density_matrix.tolist()

    def evolve_quantum_state(self, quantum_state: QuantumState,
                             unitary_op: np.ndarray) -> QuantumState:
        """
        Evolves a quantum state by applying a unitary operator.

        This represents a transformation or change in the software system, modeled
        as a unitary evolution in the quantum space.

        Args:
            quantum_state: The initial QuantumState.
            unitary_op: A numpy array representing the unitary transformation.

        Returns:
            The new QuantumState after evolution.
        """
        if unitary_op.shape[0] != self.hilbert_space_dim or \
           unitary_op.shape[1] != self.hilbert_space_dim:
            raise ValueError("Unitary operator dimension mismatch.")

        # Verify if the operator is unitary
        # U.conj().T @ U should be the identity matrix
        if not np.allclose(unitary_op.conj().T @ unitary_op, np.identity(self.hilbert_space_dim)):
            raise ValueError("The provided operator is not unitary.")

        initial_vector = np.array(quantum_state.state_vector, dtype=complex)
        evolved_vector = unitary_op @ initial_vector

        return QuantumState(
            state_vector=evolved_vector.tolist(),
            measurement_basis=quantum_state.measurement_basis
        )

    def measure_observable(self, quantum_state: QuantumState,
                           observable: np.ndarray) -> float:
        """
        Calculates the expectation value of an observable for a given quantum state.

        This corresponds to extracting a classical metric or property from the
        quantum representation of the system.

        Args:
            quantum_state: The QuantumState to measure.
            observable: A Hermitian operator (as a numpy array) representing the
                        quantity to be measured.

        Returns:
            The expectation value of the observable.
        """
        # Verify the observable is Hermitian
        if not np.allclose(observable, observable.conj().T):
            raise ValueError("The provided observable is not Hermitian.")

        state_vector = np.array(quantum_state.state_vector, dtype=complex)

        # Expectation value <psi|O|psi>
        expectation_value = (state_vector.conj().T @ observable @ state_vector).real

        return float(expectation_value)
<<<<<<< HEAD
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
