"""
System Orchestrator for QuantaCirc.
"""

from typing import Dict, Any, List
import numpy as np
import copy

from .types import QCState, SoftwareState, EnergyComponents
from .math_engine import MathEngine
from .two_phase_annealer import TwoPhaseAnnealer
from math_utils.distance_metrics import calculate_state_distance
from .lyapunov_monitor import LyapunovMonitor
from .convergence_engine import ConvergenceEngine, ConvergenceCriteria

class Orchestrator:
    """
    Coordinates the entire optimization process.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.math_engine = MathEngine(config)
        self.annealer = TwoPhaseAnnealer(config.get('annealing', {}))
        self.lyapunov_monitor = LyapunovMonitor(config.get('lyapunov', {}))
        self.convergence_engine = ConvergenceEngine(
            ConvergenceCriteria(**config.get('convergence', {}))
        )
        self.state_history: List[QCState] = []

    def run_optimization(self, initial_state: QCState, max_iterations: int) -> QCState:
        """
        Runs the main optimization loop.
        """
        self.annealer.initialize_state(initial_state)
        self.lyapunov_monitor.record_state(initial_state)
        self.state_history.append(initial_state)

        current_state = initial_state

        for i in range(max_iterations):
            self.annealer.update_temperature(i)

            # Propose a new state using a greedy local search
            new_state = self._propose_new_state(current_state)

            # Calculate energy of the new state
            total_energy, components = self.math_engine.compute_system_energy(new_state)
            new_state.energy = total_energy
            new_state.energy_components = EnergyComponents(**components)

            # Metropolis-Hastings acceptance criterion
            delta_energy = new_state.energy - current_state.energy
            if delta_energy < 0 or np.random.rand() < np.exp(-delta_energy / self.annealer.temperature):
                current_state = new_state

            # Record state and metrics
            self.lyapunov_monitor.record_state(current_state)
            self.state_history.append(current_state)

            gradient = self.math_engine.compute_gradient(current_state)
            gradient_norm = self.math_engine.gradient_norm(gradient)
            self.annealer.record_step(current_state.energy, gradient_norm)

            # Check for phase switch
            if self.annealer.phase == "A":
                self.annealer.check_phase_switch(i)
            elif self.annealer.phase == "B":
                # Measure the contraction factor λ
                if len(self.state_history) >= 3:
                    s_k = self.state_history[-1]
                    s_k_minus_1 = self.state_history[-2]
                    s_k_minus_2 = self.state_history[-3]

                    dist_k = calculate_state_distance(s_k, s_k_minus_1)
                    dist_k_minus_1 = calculate_state_distance(s_k_minus_1, s_k_minus_2)

                    if dist_k_minus_1 > 1e-9:
                        factor = dist_k / dist_k_minus_1
                        self.annealer.contraction_factor_history.append(factor)

            # Check for convergence
            if self.convergence_engine.check_convergence(self.state_history, self.lyapunov_monitor, self.annealer)['converged']:
                print(f"Convergence reached at iteration {i}.")
                break

        return current_state

    def _propose_new_state(self, current_state: QCState) -> QCState:
        """
        Proposes a new state by performing a simple greedy local search.
        It generates a few candidate states and returns the one with the lowest energy.
        """
        candidates = []
        num_candidates = 5

        for _ in range(num_candidates):
            candidate_state = copy.deepcopy(current_state)

            # Make a small random change to the candidate state
            if candidate_state.modules:
                module_idx = np.random.randint(0, len(candidate_state.modules))
                candidate_state.modules[module_idx] += np.random.choice([" ", "\n", "#"])

            if candidate_state.constraints:
                constraint_idx = np.random.randint(0, len(candidate_state.constraints))
                candidate_state.constraints[constraint_idx]['value'] += np.random.randn() * 0.1

            # Evaluate the energy of the candidate
            energy, _ = self.math_engine.compute_system_energy(candidate_state)
            candidate_state.energy = energy
            candidates.append(candidate_state)

        # Return the candidate with the lowest energy
        best_candidate = min(candidates, key=lambda s: s.energy)
        return best_candidate