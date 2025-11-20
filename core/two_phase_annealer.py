# core/two_phase_annealer.py
<<<<<<< HEAD
<<<<<<< HEAD
"""
Implements the Two-Phase Annealing optimization algorithm as described in
Part 4 of the QuantaCirc project plan.

This module provides a simulated annealer that separates the optimization
process into two distinct phases:
1. Phase A: Global exploration with a slow, logarithmic cooling schedule
   to find promising basins of the energy landscape.
2. Phase B: Local refinement with a faster, exponential cooling schedule
   to efficiently find the minimum within a basin.
"""

import math
import numpy as np
from typing import List, Optional, Dict, Any

from .types import QCState

class TwoPhaseAnnealer:
    """
    Manages a two-phase simulated annealing process. This class is designed
    to be used by a master orchestrator, which drives the main optimization loop.
    This annealer provides the logic for temperature scheduling, phase switching,
    and acceptance criteria.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the annealer with configuration.

        Args:
            config: A dictionary containing annealing parameters.
                Expected keys: 'initial_temp', 'min_temp', 'phase_a_cooling_const',
                'phase_b_cooling_rate', 'phase_switch_window', 'convergence_window',
                'convergence_tolerance'.
        """
        self.initial_temp = config.get("initial_temp", 10.0)
        self.min_temp = config.get("min_temp", 0.01)
        self.phase_a_cooling_const = config.get("phase_a_cooling_const", 10.0) # 'c' in the formula
        self.phase_b_cooling_rate = config.get("phase_b_cooling_rate", 0.98)
        self.phase_switch_window = config.get("phase_switch_window", 50)
        self.convergence_window = config.get("convergence_window", 30)
        self.convergence_tolerance = config.get("convergence_tolerance", 1e-5)

        self.temperature = self.initial_temp
        self.phase = "A"
        self.current_state: Optional[QCState] = None
        self.energy_history: List[float] = []

    def initialize_state(self, initial_state: QCState):
        """Sets the initial state for the annealing process."""
        self.current_state = initial_state
        self.temperature = self.initial_temp
        self.phase = "A"
        self.energy_history = [initial_state.energy]

    def should_accept(self, new_energy: float, old_energy: float) -> bool:
        """
        Decides whether to accept a new state using the Metropolis-Hastings criterion.
        """
        if new_energy < old_energy:
            return True

        # Avoid division by zero at low temperatures
        if self.temperature < 1e-9:
            return False

        acceptance_probability = math.exp((old_energy - new_energy) / self.temperature)
        return np.random.rand() < acceptance_probability

    def update_annealer_state(self, iteration: int, new_state: QCState):
        """
        Updates the annealer's internal state after a step, including temperature
        and phase checks.
        """
        self.current_state = new_state
        self.energy_history.append(new_state.energy)
        if len(self.energy_history) > self.phase_switch_window * 2:
            self.energy_history.pop(0) # Keep history from growing indefinitely

        self._update_phase_and_temperature(iteration)

    def _update_phase_and_temperature(self, iteration: int):
        """Updates the temperature based on the current phase and cooling schedule."""
        if self.phase == "A":
            if self._check_phase_switch():
                self.phase = "B"
                print(f"Switching to Phase B at iteration {iteration}.")
                # When switching, we might want to reset the temperature to a
                # specific value for the start of Phase B.
                self.temperature = self.initial_temp / 10.0 # Example reset
            else:
                # Logarithmic cooling for Phase A: T_k = c / log(k + 2)
                self.temperature = self.phase_a_cooling_const / math.log(iteration + 2)

        elif self.phase == "B":
            # Exponential cooling for Phase B
            self.temperature *= self.phase_b_cooling_rate

        self.temperature = max(self.temperature, self.min_temp)

    def _check_phase_switch(self) -> bool:
        """
        Checks if the criteria for switching from Phase A to B are met,
        based on the stabilization of energy.
        """
        if len(self.energy_history) < self.phase_switch_window:
            return False

        recent_energies = self.energy_history[-self.phase_switch_window:]

        # Criterion 1: Energy variance has dropped below a threshold.
        # This indicates we are no longer making large exploratory jumps.
        variance = np.var(recent_energies)
        variance_threshold = (self.initial_temp / 20.0)**2
        if variance > variance_threshold:
            return False

        # Criterion 2: The median of recent energy changes is consistently negative.
        # This indicates we are in a basin and generally moving downhill.
        deltas = np.diff(recent_energies)
        if np.median(deltas) >= 0:
            return False

        return True

    def check_convergence(self) -> bool:
        """
        Checks if the optimization has converged.

        Convergence is determined by the change in energy over a recent window,
        indicating a "flatlined" energy landscape.
        """
        window_size = self.convergence_window
        if len(self.energy_history) < window_size:
            return False

        recent_energies = np.array(self.energy_history[-window_size:])

        # Check for flatness using standard deviation
        energy_std = np.std(recent_energies)

        # Convergence is met if the energy has flatlined (low std dev) in the
        # final phase at the minimum temperature.
        is_converged = (self.phase == "B" and
                        self.temperature <= self.min_temp and
                        energy_std < self.convergence_tolerance)

        return is_converged
=======
=======
>>>>>>> remotes/origin/feat/core-infrastructure

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
<<<<<<< HEAD
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
