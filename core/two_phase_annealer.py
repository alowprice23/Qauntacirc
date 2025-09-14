import logging
import math
import random
import numpy as np
from typing import List, Any, Optional, Callable, Tuple

from pydantic import BaseModel
from core.data_models import SystemState, AnnealingResult, ContractionResult, PhaseMarker
from core.energy_calculator import EnergyCalculator

class TwoPhaseAnnealer:
    """
    Implements a mathematically rigorous two-phase annealing algorithm.
    Phase A: Global search with logarithmic cooling to find a basin of attraction.
    Phase B: Local refinement with exponential cooling and gradient descent.
    """
    def __init__(self,
                 energy_calculator: EnergyCalculator,
                 window_size: int = 50,
                 variance_threshold: float = 0.1,
                 gradient_norm_threshold: float = 1e-3,
                 gradient_variance_threshold: float = 1e-5,
                 convergence_tolerance: float = 1e-6,
                 cooling_schedule_type: str = 'logarithmic'):
        self.energy_calculator = energy_calculator
        self.window_size = window_size
        self.variance_threshold = variance_threshold
        self.gradient_norm_threshold = gradient_norm_threshold # Used for basin quality, not detection
        self.gradient_variance_threshold = gradient_variance_threshold
        self.convergence_tolerance = convergence_tolerance
        self.cooling_schedule_type = cooling_schedule_type

        self.energy_history: List[float] = []
        self.state_history: List[SystemState] = []
        self.gradient_history: List[np.ndarray] = []

    def _energy_fn(self, state: SystemState) -> float:
        """Helper to get total energy from the energy calculator."""
        return self.energy_calculator.compute_total_energy(state).total

    def _compute_temperature_constant(self, state: SystemState) -> float:
        """
        Computes the cooling constant 'c' for the logarithmic schedule.
        Heuristic: Choose c such that the initial acceptance probability for a
        characteristic "bad" move (uphill) is around 0.8.
        """
        initial_energy = self._energy_fn(state)
        uphill_deltas = []
        for _ in range(10):
            proposal = self._generate_proposals(state, num_proposals=1)[0]
            delta_e = self._energy_fn(proposal) - initial_energy
            if delta_e > 0:
                uphill_deltas.append(delta_e)

        if not uphill_deltas:
            return 1.0  # Default if no uphill moves found

        avg_delta_e = np.mean(uphill_deltas)
        # T_0 = -delta_E / log(P_accept)
        t0 = -avg_delta_e / np.log(0.8)
        # c = T_0 * log(2) for T_k = c / log(k+2)
        c = t0 * np.log(2)
        return c

    def _generate_proposals(self, state: SystemState, num_proposals: int = 10, perturbation_scale: float = 0.1) -> List[SystemState]:
        """Generates a list of proposal states by perturbing the current state."""
        proposals = []
        for _ in range(num_proposals):
            new_state = state.model_copy(deep=True)
            if not new_state.modules:
                continue

            module_to_change = random.choice(new_state.modules)
            change = random.normalvariate(0, perturbation_scale)
            module_to_change.cyclomatic_complexity = max(0, module_to_change.cyclomatic_complexity + change)
            proposals.append(new_state)
        return proposals

    def _check_invariants(self, state: SystemState) -> bool:
        """Checks if the state satisfies all hard constraints."""
        for constraint in state.constraints:
            if constraint.evaluate_violation(state) > 0:
                return False
        return True

    def _basin_detected(self) -> bool:
        """
        Detect basin entry via:
        1. Energy variance drops below threshold
        2. Gradient norm variance drops below threshold (stabilizes)
        3. No constraint violations for window
        """
        # Check if we have enough history to make a decision
        history_window = self.window_size // 10
        if len(self.energy_history) < self.window_size or len(self.gradient_history) < history_window:
            return False

        recent_energies = self.energy_history[-self.window_size:]
        energy_variance = np.var(recent_energies)

        recent_gradient_norms = [np.linalg.norm(g) for g in self.gradient_history[-history_window:]]
        gradient_norm_variance = np.var(recent_gradient_norms)

        return (energy_variance < self.variance_threshold and
                gradient_norm_variance < self.gradient_variance_threshold and
                all(self._check_invariants(s) for s in self.state_history[-self.window_size:]))

    def phase_a_search(self, initial_state: SystemState, max_iterations: int = 10000) -> Tuple[SystemState, PhaseMarker]:
        """
        Logarithmic cooling: T_k = c / log(k + 2)

        Theorem (Basin Capture): P(reach global basin) ≥ 1-δ
        for sufficient iterations and proper cooling constant c
        """
        state = initial_state.model_copy(deep=True)

        if self.cooling_schedule_type == 'logarithmic':
            temperature_constant = self._compute_temperature_constant(state)
        else: # exponential for testing
            temperature_constant = 50.0
            alpha = 0.95

        for k in range(max_iterations):
            if self.cooling_schedule_type == 'logarithmic':
                temperature = temperature_constant / np.log(k + 2)
            else:
                temperature = temperature_constant * (alpha ** k)

            proposals = self._generate_proposals(state)

            current_energy = self._energy_fn(state)
            for proposal in proposals:
                delta_e = self._energy_fn(proposal) - current_energy

                accept_prob = min(1.0, np.exp(-delta_e / temperature)) if temperature > 1e-9 else 0.0
                if np.random.random() < accept_prob:
                    state = proposal
                    current_energy += delta_e

            self.energy_history.append(current_energy)
            self.state_history.append(state.model_copy(deep=True))

            # Infrequently compute and store gradient for basin detection
            if k > 0 and k % 10 == 0:
                gradient = self._compute_numerical_gradient(state, self._energy_fn)
                self.gradient_history.append(gradient)
                if self._basin_detected():
                    logging.info(f"Basin captured at iteration {k}.")
                    return state, PhaseMarker.BASIN_CAPTURED

        logging.warning("Phase A reached max iterations without capturing a basin.")
        return state, PhaseMarker.MAX_ITERATIONS_REACHED

    def _compute_numerical_gradient(self, state: SystemState, energy_fn: Callable[[SystemState], float], h: float = 1e-6) -> np.ndarray:
        """
        Computes the gradient of the energy function numerically.
        The gradient is computed with respect to the cyclomatic complexity of each module.
        """
        if not state.modules:
            return np.array([])

        gradient = np.zeros(len(state.modules))
        for i, module in enumerate(state.modules):
            # Create a fresh copy for each perturbation to avoid cumulative changes
            state_copy = state.model_copy(deep=True)

            # Perturb plus
            state_plus_h = state_copy.model_copy(deep=True)
            state_plus_h.modules[i].cyclomatic_complexity += h
            energy_plus_h = energy_fn(state_plus_h)

            # Perturb minus
            state_minus_h = state_copy.model_copy(deep=True)
            state_minus_h.modules[i].cyclomatic_complexity -= h
            energy_minus_h = energy_fn(state_minus_h)

            gradient[i] = (energy_plus_h - energy_minus_h) / (2 * h)

        return gradient

    def compute_pl_constant(self, state: SystemState, energy_fn: Callable[[SystemState], float]) -> float:
        """
        Estimates the Polyak-Łojasiewicz (PL) constant μ for the energy function.
        """
        if not state.modules:
            return 1.0  # Default value if no modules

        # Define the space for cyclomatic complexity values
        space = (0, 100, len(state.modules))

        # We need an approximation of the optimal state x*
        # For this implementation, we'll assume the current state is close to optimal
        # and use it as a proxy. This is a simplification.
        x_optimal = np.array([m.cyclomatic_complexity for m in state.modules])

        def func(x: np.ndarray) -> float:
            s = state.model_copy(deep=True)
            for i, mod in enumerate(s.modules):
                mod.cyclomatic_complexity = x[i]
            return energy_fn(s)

        def grad_func(x: np.ndarray) -> np.ndarray:
            s = state.model_copy(deep=True)
            for i, mod in enumerate(s.modules):
                mod.cyclomatic_complexity = x[i]
            return self._compute_numerical_gradient(s, energy_fn)

        # In a real scenario, we would need a better way to find x_optimal
        # For now, we proceed with the estimation based on the current state.
        from math_utils.pl_inequality import verify_pl_inequality
        is_pl, mu = verify_pl_inequality(func, grad_func, x_optimal, space, samples=100)

        return mu if is_pl and mu > 1e-6 else 1.0 # Return a default if not PL or mu is too small

    def _gradient_step(self, state: SystemState, step_size: float) -> SystemState:
        """Performs a single gradient descent step."""
        gradient = self._compute_numerical_gradient(state, self._energy_fn)
        new_state = state.model_copy(deep=True)

        for i, module in enumerate(new_state.modules):
            module.cyclomatic_complexity -= step_size * gradient[i]
            module.cyclomatic_complexity = max(0, module.cyclomatic_complexity) # Ensure non-negative

        return new_state

    def _measure_state_distance(self, state1: SystemState, state2: SystemState) -> float:
        """Measures the Euclidean distance between the complexity vectors of two states."""
        if not state1.modules or not state2.modules:
            return 0.0
        vec1 = np.array([m.cyclomatic_complexity for m in state1.modules])
        vec2 = np.array([m.cyclomatic_complexity for m in state2.modules])
        return np.linalg.norm(vec1 - vec2)

    def _converged(self, state: SystemState, tolerance: float) -> bool:
        """Checks if the optimization has converged."""
        gradient = self._compute_numerical_gradient(state, self._energy_fn)
        return np.linalg.norm(gradient) < tolerance

    def phase_b_refinement(self, state: SystemState, max_iterations: int = 5000) -> "OptimizationResult":
        """
        Exponential cooling with PL-based contraction

        Theorem (Geometric Convergence):
        E(S_k) - E* ≤ (1-ημ)^k (E(S_0) - E*)
        where μ is the PL constant
        """
        from core.data_models import OptimizationResult

        pl_constant = self.compute_pl_constant(state, self._energy_fn)
        step_size = min(0.1, 1.8 / pl_constant)  # Ensure η < 2/μ

        contraction_history = []
        self._prev_state = state.model_copy(deep=True) # For contraction measurement

        for k in range(max_iterations):
            old_state = state.model_copy(deep=True)
            state = self._gradient_step(state, step_size)

            # Measure contraction factor
            dist_old_prev = self._measure_state_distance(old_state, self._prev_state)
            if dist_old_prev > 1e-9:
                contraction = self._measure_state_distance(state, old_state) / dist_old_prev
                contraction_history.append(contraction)

            self._prev_state = old_state

            # Verify contraction condition λ < 1
            if len(contraction_history) >= 10:
                avg_contraction = np.mean(contraction_history[-10:])
                if avg_contraction < 0.95:
                    logging.info(f"Contraction verified: λ = {avg_contraction:.3f}")
                else:
                    logging.warning(f"Contraction violation: λ = {avg_contraction:.3f}")

            # Check convergence
            if self._converged(state, tolerance=self.convergence_tolerance):
                return OptimizationResult(
                    final_state=state,
                    iterations=k,
                    contraction_factor=np.mean(contraction_history[-10:]) if contraction_history else None,
                    convergence_status="CONVERGED"
                )

        logging.warning("Phase B reached max iterations without converging.")
        return OptimizationResult(
            final_state=state,
            iterations=max_iterations,
            contraction_factor=np.mean(contraction_history[-10:]) if contraction_history else None,
            convergence_status="MAX_ITERATIONS_REACHED"
        )

    def optimize(self, initial_state: SystemState, phase_a_max_iter: int = 10000, phase_b_max_iter: int = 5000) -> "OptimizationResult":
        """
        Runs the full two-phase optimization process.
        """
        from core.data_models import OptimizationResult

        # Phase A: Global Search
        basin_state, phase_a_result = self.phase_a_search(initial_state, max_iterations=phase_a_max_iter)

        phase_a_iterations = len(self.energy_history)

        if phase_a_result == PhaseMarker.BASIN_CAPTURED:
            # Phase B: Local Refinement
            result = self.phase_b_refinement(basin_state, max_iterations=phase_b_max_iter)
            result.phase_switch_point = phase_a_iterations
            return result
        else:
            # Phase A failed to find a basin
            return OptimizationResult(
                final_state=basin_state,
                iterations=phase_a_iterations,
                convergence_status="FAILED_IN_PHASE_A",
                phase_switch_point=None
            )
