# core/functor.py

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
