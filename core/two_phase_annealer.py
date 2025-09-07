# core/two_phase_annealer.py

"""
Implements the Two-Phase Annealing optimization algorithm.

This module provides an annealer that separates the optimization process into
two distinct phases:
1. Phase A (Exploration): High-temperature phase to broadly explore the state space.
2. Phase B (Exploitation): Low-temperature phase to fine-tune and find local optima.
"""

from __future__ import annotations

import math
import random
from typing import Callable, Optional

from core.types import QCState
from math_utils import annealing, contractive_maps
from core.energy_calculator import EnergyCalculator

# Type alias for a function that proposes a new state
StateProposalFunc = Callable[[QCState], QCState]

class TwoPhaseAnnealer:
    """
    Manages a two-phase simulated annealing process for state optimization.

    This annealer uses two different temperature schedules and acceptance criteria
    to balance exploration of the energy landscape with exploitation of promising
    regions.
    """

    def __init__(self,
                 energy_calculator: EnergyCalculator,
                 propose_new_state: StateProposalFunc,
                 phase_a_schedule: annealing.TemperatureSchedule,
                 phase_b_schedule: annealing.TemperatureSchedule,
                 phase_transition_temp: float):
        """
        Initializes the TwoPhaseAnnealer.

        Args:
            energy_calculator: An instance of EnergyCalculator to compute state energy.
            propose_new_state: A function that takes a state and proposes a new one.
            phase_a_schedule: Temperature schedule for the exploration phase.
            phase_b_schedule: Temperature schedule for the exploitation phase.
            phase_transition_temp: The temperature at which to switch from Phase A to B.
        """
        self.energy_calculator = energy_calculator
        self.propose_new_state = propose_new_state
        self.phase_a_schedule = phase_a_schedule
        self.phase_b_schedule = phase_b_schedule
        self.phase_transition_temp = phase_transition_temp

        self.current_state: Optional[QCState] = None
        self.current_energy: Optional[float] = None
        self.best_state: Optional[QCState] = None
        self.best_energy: float = float('inf')

        self.phase: str = "A"
        self.temperature: float = self.phase_a_schedule.initial_temp

    def initialize_state(self, initial_state: QCState):
        """
        Sets the initial state for the annealing process.

        Args:
            initial_state: The starting QCState.
        """
        self.current_state = initial_state
        self.current_energy = initial_state.energy
        self.best_state = initial_state
        self.best_energy = initial_state.energy
        self.temperature = self.phase_a_schedule.get_temperature(0)

    def step(self, iteration: int) -> QCState:
        """
        Performs a single step of the annealing process.

        This involves proposing a new state, deciding whether to accept it,
        and updating the temperature.

        Args:
            iteration: The current iteration number.

        Returns:
            The current QCState after the step.
        """
        if self.current_state is None:
            raise RuntimeError("Annealer has not been initialized with a state.")

        # Determine phase and update temperature
        self._update_phase_and_temperature(iteration)

        # Propose a new state
        new_state = self.propose_new_state(self.current_state)

        # Calculate energy of the new state
        # In a real implementation, metrics would be calculated first.
        # Here, we assume new_state comes with pre-computed energy for simplicity.
        new_energy = new_state.energy

        # Decide whether to accept the new state
        if self._should_accept(new_energy, self.current_energy, self.temperature):
            self.current_state = new_state
            self.current_energy = new_energy

            # Update best state found so far
            if new_energy < self.best_energy:
                self.best_state = new_state
                self.best_energy = new_energy

        return self.current_state

    def _update_phase_and_temperature(self, iteration: int):
        """Updates the current phase and temperature."""
        if self.phase == "A":
            self.temperature = self.phase_a_schedule.get_temperature(iteration)
            if self.temperature <= self.phase_transition_temp:
                self.phase = "B"
                # Reset iteration count for the new phase's schedule
                self.phase_b_schedule.reset()
                self.temperature = self.phase_b_schedule.get_temperature(0)
        else: # Phase B
            self.temperature = self.phase_b_schedule.get_temperature(iteration)

    @staticmethod
    def _should_accept(new_energy: float, current_energy: float, temp: float) -> bool:
        """
        Metropolis-Hastings acceptance criterion.

        Args:
            new_energy: Energy of the proposed new state.
            current_energy: Energy of the current state.
            temp: Current temperature.

        Returns:
            True if the new state should be accepted, False otherwise.
        """
        if new_energy < current_energy:
            return True

        if temp < 1e-9: # Avoid division by zero at very low temperatures
            return False

        acceptance_prob = math.exp((current_energy - new_energy) / temp)
        return random.random() < acceptance_prob

    def phase_a_step(self, iteration: int) -> QCState:
        """
        Performs a step specifically in the high-temperature exploration phase.

        This method is provided for more granular control over the annealing process.

        Args:
            iteration: The current exploration phase iteration.

        Returns:
            The current state after the step.
        """
        if self.phase != "A":
            raise RuntimeError("Cannot perform Phase A step while in Phase B.")

        self.temperature = self.phase_a_schedule.get_temperature(iteration)
        return self.step(iteration)

    def phase_b_step(self, iteration: int) -> QCState:
        """
        Performs a step specifically in the low-temperature exploitation phase.

        This method is provided for more granular control over the annealing process.

        Args:
            iteration: The current exploitation phase iteration.

        Returns:
            The current state after the step.
        """
        if self.phase != "B":
            raise RuntimeError("Cannot perform Phase B step while in Phase A.")

        self.temperature = self.phase_b_schedule.get_temperature(iteration)
        return self.step(iteration)

    def check_convergence(self, state_history: list[QCState]) -> bool:
        """
        Checks for convergence using contractive mapping principles.

        If the sequence of states generated by the annealer forms a contractive
        mapping in the state space, it is guaranteed to converge to a unique
        fixed point.

        Args:
            state_history: A recent history of QCStates.

        Returns:
            True if convergence is detected, False otherwise.
        """
        if len(state_history) < 2:
            return False

        # We need a way to represent states as points in a metric space.
        # We can use their energy or a vector of key metrics.
        # Here, we'll use the energy as a simple 1D representation.

        points = [s.energy for s in state_history]

        # A simplified check: if the process is contractive, the distance
        # between successive points should decrease.
        is_contractive, lipschitz_constant = contractive_maps.is_contractive_sequence(points)

        # We can declare convergence if the mapping is contractive and the
        # rate of change is very small.
        if is_contractive:
            if len(points) > 1:
                last_change = abs(points[-1] - points[-2])
                if last_change < 1e-7: # Threshold for change
                    return True
        return False

    @property
    def is_finished(self) -> bool:
        """
        Checks if the annealing process has completed.

        Returns:
            True if the temperature has reached its minimum in Phase B.
        """
        return self.phase == "B" and self.temperature <= self.phase_b_schedule.min_temp
