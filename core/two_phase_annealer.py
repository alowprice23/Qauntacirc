# core/two_phase_annealer.py
"""
Implements the Two-Phase Annealing optimization algorithm as described in
Part 4 of the QuantaCirc project plan.
"""

import math
import numpy as np
from typing import List, Optional, Dict, Any

from .types import QCState
from math_utils.annealing import TemperatureSchedule
from math_utils.contractive_maps import is_contraction_mapping

class TwoPhaseAnnealer:
    """
    Manages a two-phase simulated annealing process.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.phase_a_schedule = TemperatureSchedule(
            initial_temp=config.get("initial_temp", 1000.0),
            schedule_type='logarithmic'
        )
        self.phase_b_schedule = TemperatureSchedule(
            initial_temp=config.get("phase_b_start_temp", 100.0),
            final_temp=config.get("min_temp", 0.1),
            steps=config.get("phase_b_steps", 1000),
            schedule_type='exponential'
        )
        self.phase_switch_window = config.get("phase_switch_window", 50)
        self.convergence_tolerance = config.get("convergence_tolerance", 1e-5)

        self.phase = "A"
        self.temperature = self.phase_a_schedule.initial_temp
        self.energy_history: List[float] = []
        self.gradient_norm_history: List[float] = []
        self.contraction_factor_history: List[float] = []
        self.phase_switch_iteration: int = -1

    def initialize_state(self, initial_state: QCState):
        self.phase = "A"
        self.temperature = self.phase_a_schedule.initial_temp
        self.energy_history = [initial_state.energy]
        self.gradient_norm_history = []
        self.contraction_factor_history = []
        self.phase_switch_iteration = -1

    def update_temperature(self, iteration: int):
        """Updates the temperature based on the current phase and schedule."""
        if self.phase == "A":
            self.temperature = self.phase_a_schedule.get_temperature(iteration)
        else: # Phase B
            # Phase B step counting should be relative to the start of Phase B
            phase_b_iter = iteration - self.phase_switch_iteration
            self.temperature = self.phase_b_schedule.get_temperature(phase_b_iter)

        self.temperature = max(self.temperature, self.config.get("min_temp", 0.1))

    def check_phase_switch(self, iteration: int) -> bool:
        """
        Checks if the criteria for switching from Phase A to B are met.
        Basin capture detection via gradient magnitude and variance stabilization.
        """
        if len(self.energy_history) < self.phase_switch_window:
            return False

        # Criterion 1: Variance stabilization
        recent_energies = self.energy_history[-self.phase_switch_window:]
        energy_variance = np.var(recent_energies)
        variance_threshold = self.config.get("phase_switch_variance_threshold", 0.1)
        if energy_variance > variance_threshold:
            return False

        # Criterion 2: Gradient magnitude stabilization
        if len(self.gradient_norm_history) < self.phase_switch_window:
            return False
        recent_gradients = self.gradient_norm_history[-self.phase_switch_window:]
        gradient_mean = np.mean(recent_gradients)
        gradient_threshold = self.config.get("phase_switch_gradient_threshold", 0.01)
        if gradient_mean > gradient_threshold:
            return False

        print(f"Switching to Phase B at iteration {iteration}.")
        self.phase = "B"
        self.phase_switch_iteration = iteration
        return True

    def measure_contraction_factor(self, state_transformer_func, space_definition):
        """
        Measures the contraction factor λ of the state transformation function.
        """
        is_contraction, factor = is_contraction_mapping(
            state_transformer_func,
            space_definition,
            samples=self.config.get("contraction_samples", 100)
        )
        if is_contraction:
            self.contraction_factor_history.append(factor)
        return factor

    def check_convergence(self) -> bool:
        """
        Checks for convergence in Phase B.
        """
        if self.phase != "B":
            return False

        # Criterion 1: Contraction factor consistently < 1
        if len(self.contraction_factor_history) < self.phase_switch_window:
            return False
        recent_factors = self.contraction_factor_history[-self.phase_switch_window:]
        if np.mean(recent_factors) >= 1.0:
            return False

        # Criterion 2: Energy has stabilized
        if len(self.energy_history) < self.phase_switch_window:
            return False
        recent_energies = self.energy_history[-self.phase_switch_window:]
        if np.std(recent_energies) > self.convergence_tolerance:
            return False

        return True

    def record_step(self, energy: float, gradient_norm: float):
        self.energy_history.append(energy)
        self.gradient_norm_history.append(gradient_norm)
        # Keep history from growing indefinitely
        if len(self.energy_history) > self.phase_switch_window * 2:
            self.energy_history.pop(0)
            self.gradient_norm_history.pop(0)
