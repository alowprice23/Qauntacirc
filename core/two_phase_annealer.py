# core/two_phase_annealer.py
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

        if self.phase == "B":
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
        if len(self.energy_history) < self.convergence_window:
            return False

        recent_energies = self.energy_history[-self.convergence_window:]
        energy_change = abs(np.mean(recent_energies[:10]) - np.mean(recent_energies[-10:]))

        # Also check if we are in the final phase at a very low temperature
        if self.phase == "B" and self.temperature == self.min_temp:
             if energy_change < self.convergence_tolerance:
                return True

        return False
