# core/state_space.py

"""
Defines the state space of the quantum-mechanical system.

This module provides classes and functions to describe the geometry and
properties of the Hilbert space in which the system's quantum state resides.
"""

from __future__ import annotations

import numpy as np
from typing import List, Tuple

from core.types import QCState

class StateSpace:
    """
    Represents the state space of the software system's quantum representation.

    This class provides methods to analyze the properties of the state space,
    such as its dimension, and to compute relationships between states, like
    distances and transition paths.
    """

    def __init__(self, dimension: int):
        """
        Initializes the StateSpace.

        Args:
            dimension: The dimension of the Hilbert space. This should match
                       the dimension used by the Functor.
        """
        if dimension <= 0:
            raise ValueError("State space dimension must be positive.")
        self.dimension = dimension

    def get_dimension(self) -> int:
        """
        Returns the dimension of the state space.
        """
        return self.dimension

    def is_valid_state(self, state: QCState) -> bool:
        """
        Checks if a given QCState is valid within this state space.

        A valid state must have a quantum state vector whose length matches
        the dimension of the space and is properly normalized.

        Args:
            state: The QCState to validate.

        Returns:
            True if the state is valid, False otherwise.
        """
        if not state.quantum_state:
            return False

        q_state = state.quantum_state
        if len(q_state.state_vector) != self.dimension:
            return False

        # Check for normalization
        norm = np.linalg.norm(q_state.state_vector)
        return np.isclose(norm, 1.0)

    def compute_distance(self, state_a: QCState, state_b: QCState, metric: str = 'fidelity') -> float:
        """
        Computes the distance between two states in the state space.

        Several metrics can be used, such as fidelity-based distance or
        simple Euclidean distance on the state vectors.

        Args:
            state_a: The first QCState.
            state_b: The second QCState.
            metric: The distance metric to use ('fidelity' or 'euclidean').

        Returns:
            The computed distance between the two states.
        """
        if not self.is_valid_state(state_a) or not self.is_valid_state(state_b):
            raise ValueError("One or both states are not valid for this state space.")

        vec_a = np.array(state_a.quantum_state.state_vector)
        vec_b = np.array(state_b.quantum_state.state_vector)

        if metric == 'fidelity':
            # Fidelity F = |<a|b>|^2
            fidelity = np.abs(np.vdot(vec_a, vec_b))**2
            # A common distance measure is D = sqrt(1 - F)
            return np.sqrt(1 - fidelity)
        elif metric == 'euclidean':
            return np.linalg.norm(vec_a - vec_b)
        else:
            raise ValueError(f"Unsupported distance metric: {metric}")

    def get_random_state_vector(self) -> List[complex]:
        """
        Generates a random, normalized state vector in the Hilbert space.

        This is useful for initialization or testing purposes.

        Returns:
            A list of complex numbers representing a random state vector.
        """
        # Generate a random complex vector from a standard normal distribution
        random_vector = (np.random.randn(self.dimension) +
                         1j * np.random.randn(self.dimension))

        # Normalize it
        norm = np.linalg.norm(random_vector)
        normalized_vector = random_vector / norm

        return normalized_vector.tolist()

    def get_basis_vector(self, index: int) -> List[complex]:
        """
        Returns a specific basis vector (e.g., |0>, |1>, ...).

        Args:
            index: The index of the basis vector to retrieve.

        Returns:
            A list of complex numbers for the basis vector.
        """
        if not (0 <= index < self.dimension):
            raise IndexError("Basis vector index is out of bounds.")

        basis_vector = np.zeros(self.dimension, dtype=complex)
        basis_vector[index] = 1.0

        return basis_vector.tolist()

# Example Usage
if __name__ == '__main__':
    from uuid import uuid4
    from datetime import datetime
    from core.types import SoftwareState, QuantumState, EnergyComponents

    # Define a 4-dimensional state space (like a 2-qubit system)
    space = StateSpace(dimension=4)
    print(f"State space initialized with dimension: {space.get_dimension()}")

    # Create two valid states
    state_vec_a = space.get_basis_vector(0) # |00>
    state_vec_b = space.get_random_state_vector()

    # We need to wrap them in QCState objects to use the methods
    dummy_sw_state = SoftwareState(component_versions={}, config_hashes={}, status="nominal")
    dummy_energy_comps = EnergyComponents(static=0, dynamic=0, interaction=0)

    qc_state_a = QCState(
        id=uuid4(),
        timestamp=datetime.utcnow(),
        software_state=dummy_sw_state,
        quantum_state=QuantumState(state_vector=state_vec_a, density_matrix=None),
        energy=0, energy_components=dummy_energy_comps, lyapunov_potential=0, contraction_factor=1.0,
        optimization_phase="N/A"
    )

    qc_state_b = QCState(
        id=uuid4(),
        timestamp=datetime.utcnow(),
        software_state=dummy_sw_state,
        quantum_state=QuantumState(state_vector=state_vec_b, density_matrix=None),
        energy=0, energy_components=dummy_energy_comps, lyapunov_potential=0, contraction_factor=1.0,
        optimization_phase="N/A"
    )

    print(f"\nIs state A valid? {space.is_valid_state(qc_state_a)}")
    print(f"Is state B valid? {space.is_valid_state(qc_state_b)}")

    # Calculate distances
    dist_fidelity = space.compute_distance(qc_state_a, qc_state_b, metric='fidelity')
    dist_euclidean = space.compute_distance(qc_state_a, qc_state_b, metric='euclidean')

    print(f"\nDistance (fidelity-based) between A and B: {dist_fidelity:.4f}")
    print(f"Distance (Euclidean) between A and B: {dist_euclidean:.4f}")

    # Create an invalid state
    invalid_vec = [1.0, 2.0, 3.0, 4.0] # Not normalized
    invalid_qc_state = QCState(
        id=uuid4(),
        timestamp=datetime.utcnow(),
        software_state=dummy_sw_state,
        quantum_state=QuantumState(state_vector=invalid_vec, density_matrix=None),
        energy=0, energy_components=dummy_energy_comps, lyapunov_potential=0, contraction_factor=1.0,
        optimization_phase="N/A"
    )
    print(f"\nIs invalid state valid? {space.is_valid_state(invalid_qc_state)}")
