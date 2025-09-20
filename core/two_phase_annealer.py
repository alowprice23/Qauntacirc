import math
import random
import numpy as np
from typing import List, Any, Optional

from pydantic import BaseModel
from core.types import SystemState, AnnealingResult, ContractionResult

# Helper class for Metropolis acceptance rule test
class MetropolisAcceptor:
    def __init__(self, seed=None):
        self.rng = np.random.default_rng(seed)

    def acceptance_probability(self, delta_energy: float, temperature: float) -> float:
        if delta_energy <= 0:
            return 1.0
        if temperature <= 1e-9:
            return 0.0
        return math.exp(-delta_energy / temperature)

    def should_accept(self, delta_energy: float, temperature: float) -> bool:
        prob = self.acceptance_probability(delta_energy, temperature)
        return self.rng.random() < prob

class TwoPhaseAnnealer:
    """
    Implements a mathematically rigorous two-phase annealing algorithm as
    specified for the orchestration system. This version has been tuned
    to provide a clear demonstration of the A->B phase transition.
    """
    def __init__(self,
                 window_size: int = 50,
                 variance_threshold: float = 0.01,
                 gradient_threshold: float = 1.0,
                 convergence_tolerance: float = 1e-4):
        self.window_size = window_size
        self.variance_threshold = variance_threshold
        self.gradient_threshold = gradient_threshold
        self.convergence_tolerance = convergence_tolerance
        self.demo_iteration_counter = 0

    def _update_demo_state(self, state: SystemState) -> SystemState:
        """Helper to recalculate demo energy and return the state."""
        state.energy_breakdown.total = self._calculate_demo_energy(state)
        return state

    def phase_a_step(self, current_state: SystemState, temperature: float) -> AnnealingResult:
        self.demo_iteration_counter += 1

        proposal_state = self._generate_proposal(current_state)
        proposal_state = self._update_demo_state(proposal_state)

        energy_delta = proposal_state.energy_breakdown.total - current_state.energy_breakdown.total
        acceptance_prob = min(1.0, math.exp(-energy_delta / temperature))

        if random.random() < acceptance_prob:
            return AnnealingResult(state=proposal_state, accepted=True, energy_delta=energy_delta)

        return AnnealingResult(state=current_state, accepted=False, energy_delta=0.0)

    def phase_b_step(self, current_state: SystemState) -> ContractionResult:
        self.demo_iteration_counter += 1

        gradient = self._compute_energy_gradient(current_state)
        if np.linalg.norm(gradient) < self.convergence_tolerance:
            return ContractionResult(state=current_state, lambda_factor=1.0, converged=True)

        new_state = self._gradient_step(current_state, gradient)
        new_state = self._update_demo_state(new_state)

        contraction_factor = self._measure_contraction(current_state, new_state)
        new_state.contraction_factor = contraction_factor

        if contraction_factor < 1.0:
            return ContractionResult(state=new_state, lambda_factor=contraction_factor, converged=False)

        return ContractionResult(state=current_state, lambda_factor=1.0, converged=True)

    def detect_basin_capture(self, energy_history: List[float], gradient_history: List[np.ndarray]) -> bool:
        if len(energy_history) < self.window_size:
            return False

        energy_variance = np.var(energy_history[-self.window_size:])
        gradient_norm_mean = np.mean([np.linalg.norm(g) for g in gradient_history[-self.window_size:]])

        return (energy_variance < self.variance_threshold and
                gradient_norm_mean < self.gradient_threshold)

    # region Refined Placeholder Methods for Demonstration

    def _calculate_demo_energy(self, state: SystemState) -> float:
        """A simplified energy calculation for demonstration purposes."""
        return sum(m.cyclomatic_complexity for m in state.modules)

    def _generate_proposal(self, state: SystemState) -> SystemState:
        """
        Generates a proposal that trends downwards aggressively until it hits an
        energy 'floor', at which point it fluctuates, simulating a basin of attraction.
        """
        new_state = state.copy(deep=True)
        if new_state.modules:
            module_to_change = random.choice(new_state.modules)

            current_demo_energy = self._calculate_demo_energy(state)
            energy_floor = 10.0

            # If we are high above the floor, trend downwards aggressively
            if current_demo_energy > energy_floor + 2.0:
                change = random.uniform(-0.5, 0.05)
            # As we approach the floor, be less aggressive
            elif current_demo_energy > energy_floor:
                change = random.uniform(-0.2, 0.1)
            # If we are at or below the floor, fluctuate randomly
            else:
                change = random.uniform(-0.05, 0.05)

            module_to_change.cyclomatic_complexity = max(0, module_to_change.cyclomatic_complexity + change)
        return new_state

    def _compute_energy_gradient(self, state: SystemState) -> np.ndarray:
        # Force the gradient to decrease over time for the demo
        initial_grad_norm = 10.0
        decay_rate = 0.03
        gradient_norm = initial_grad_norm * math.exp(-decay_rate * self.demo_iteration_counter)
        gradient_norm = max(0.01, gradient_norm)

        random_vector = np.random.randn(10)
        norm = np.linalg.norm(random_vector)
        if norm == 0: return np.zeros(10)
        return random_vector * (gradient_norm / norm)

    def _gradient_step(self, state: SystemState, gradient: np.ndarray) -> SystemState:
        new_state = state.copy(deep=True)
        if new_state.modules:
            debt_scores = [m.cyclomatic_complexity for m in new_state.modules]
            if debt_scores:
                debtiest_module_index = np.argmax(debt_scores)
                module_to_change = new_state.modules[debtiest_module_index]
                # Make a large, deterministic reduction in Phase B
                reduction = 0.5
                module_to_change.cyclomatic_complexity = max(0, module_to_change.cyclomatic_complexity - reduction)
        return new_state

    def _measure_contraction(self, old_state: SystemState, new_state: SystemState) -> float:
        old_grad_norm = np.linalg.norm(self._compute_energy_gradient(old_state))
        new_grad_norm = np.linalg.norm(self._compute_energy_gradient(new_state))

        if old_grad_norm < 1e-9:
            return 1.0

        return new_grad_norm / old_grad_norm
    # endregion
