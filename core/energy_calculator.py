# core/energy_calculator.py

"""
Computes the energy of the quantum-mechanical system representation.

The energy function E_approx = E_static + E_dynamic + E_interaction serves as the
Hamiltonian for the system, guiding the optimization process.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Any, Optional, Tuple
from functools import lru_cache

from core.types import QCState, EnergyComponents
from math_utils import laplacian, annealing, lyapunov

# Constants for energy calculation
WEIGHT_COMPLEXITY = 1.0
WEIGHT_COUPLING = 1.5
WEIGHT_COHESION = 1.2
WEIGHT_RUNTIME_PERF = 2.0
WEIGHT_MEMORY_USAGE = 1.8
WEIGHT_INTER_MODULE_DEPS = 1.3
WEIGHT_API_SURFACE = 1.1

class EnergyCalculator:
    """
    Calculates the total energy of a software system's quantum representation.

    This class implements the core energy function, which is a sum of static,
    dynamic, and interaction components. It provides methods for computing the
    energy, its gradient, and its Hessian, which are essential for optimization
    algorithms like simulated annealing and gradient descent.

    The calculator uses a caching strategy to speed up incremental computations,
    which is crucial during the iterative optimization process.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initializes the EnergyCalculator.

        Args:
            config: Configuration dictionary for energy calculation weights.
        """
        self.config = config or {}
        self._w_complexity = self.config.get("w_complexity", WEIGHT_COMPLEXITY)
        self._w_coupling = self.config.get("w_coupling", WEIGHT_COUPLING)
        self._w_cohesion = self.config.get("w_cohesion", WEIGHT_COHESION)
        self._w_runtime_perf = self.config.get("w_runtime_perf", WEIGHT_RUNTIME_PERF)
        self._w_memory_usage = self.config.get("w_memory_usage", WEIGHT_MEMORY_USAGE)
        self._w_inter_module_deps = self.config.get("w_inter_module_deps", WEIGHT_INTER_MODULE_DEPS)
        self._w_api_surface = self.config.get("w_api_surface", WEIGHT_API_SURFACE)

    @lru_cache(maxsize=128)
    def compute_static_energy(self, metrics: Dict[str, float]) -> float:
        """
        Computes the static energy component from code metrics.

        Static energy relates to the inherent complexity and structure of the code.
        It's derived from metrics like cyclomatic complexity, coupling, and cohesion.

        Args:
            metrics: A dictionary of static code metrics.
                Expected keys: 'cyclomatic_complexity', 'coupling', 'cohesion'.

        Returns:
            The calculated static energy component.
        """
        complexity = metrics.get('cyclomatic_complexity', 0)
        coupling = metrics.get('coupling', 0)
        cohesion = metrics.get('cohesion', 1)  # Assume perfect cohesion if not provided

        # Cohesion is "good", so its contribution should be inverse
        e_static = (self._w_complexity * complexity +
                    self._w_coupling * coupling -
                    self._w_cohesion * (1 / (cohesion + 1e-6))) # add small epsilon to avoid division by zero
        return e_static

    @lru_cache(maxsize=128)
    def compute_dynamic_energy(self, metrics: Dict[str, float]) -> float:
        """
        Computes the dynamic energy component from runtime metrics.

        Dynamic energy relates to the system's behavior during execution.
        It's derived from runtime performance indicators and memory consumption.

        Args:
            metrics: A dictionary of dynamic runtime metrics.
                Expected keys: 'avg_response_time', 'peak_memory_usage'.

        Returns:
            The calculated dynamic energy component.
        """
        runtime_perf = metrics.get('avg_response_time', 0)
        memory_usage = metrics.get('peak_memory_usage', 0)

        e_dynamic = (self._w_runtime_perf * runtime_perf +
                     self._w_memory_usage * memory_usage)
        return e_dynamic

    @lru_cache(maxsize=128)
    def compute_interaction_energy(self, metrics: Dict[str, float]) -> float:
        """
        Computes the interaction energy component from dependency metrics.

        Interaction energy captures the complexity of connections between different
        parts of the system, such as modules or services.

        Args:
            metrics: A dictionary of interaction metrics.
                Expected keys: 'inter_module_dependencies', 'api_surface_area'.

        Returns:
            The calculated interaction energy component.
        """
        inter_module_deps = metrics.get('inter_module_dependencies', 0)
        api_surface_area = metrics.get('api_surface_area', 0)

        e_interaction = (self._w_inter_module_deps * inter_module_deps +
                         self._w_api_surface * api_surface_area)
        return e_interaction

    def compute_total_energy(self, static_metrics: Dict[str, float],
                             dynamic_metrics: Dict[str, float],
                             interaction_metrics: Dict[str, float]) -> Tuple[float, EnergyComponents]:
        """
        Computes the total energy and its components for a given system state.

        Args:
            static_metrics: Metrics for static energy calculation.
            dynamic_metrics: Metrics for dynamic energy calculation.
            interaction_metrics: Metrics for interaction energy calculation.

        Returns:
            A tuple containing the total energy and an EnergyComponents object.
        """
        e_static = self.compute_static_energy(static_metrics)
        e_dynamic = self.compute_dynamic_energy(dynamic_metrics)
        e_interaction = self.compute_interaction_energy(interaction_metrics)

        total_energy = e_static + e_dynamic + e_interaction
        components = EnergyComponents(
            static=e_static,
            dynamic=e_dynamic,
            interaction=e_interaction
        )
        return total_energy, components

    def energy_gradient(self, state: QCState, delta: float = 1e-5) -> np.ndarray:
        """
        Computes the gradient of the energy function at a given state.

        This is used by gradient-based optimization algorithms to find the
        direction of steepest ascent/descent. The gradient is computed using
        numerical differentiation (finite differences).

        Args:
            state: The QCState at which to compute the gradient.
            delta: The perturbation size for finite differences.

        Returns:
            A numpy array representing the energy gradient.
        """
        # This is a simplified representation. A real implementation would need
        # a way to perturb the state and re-evaluate metrics.
        # For this example, we'll use the energy components as a proxy for state params.

        params = np.array([
            state.energy_components.static,
            state.energy_components.dynamic,
            state.energy_components.interaction
        ])

        grad = np.zeros_like(params)

        for i in range(len(params)):
            params_plus = params.copy()
            params_plus[i] += delta

            # This is a mock recalculation. In a real scenario, we would
            # perturb the underlying software state, remeasure metrics,
            # and recompute energy.
            e_plus, _ = self._recompute_energy_from_params(params_plus)

            params_minus = params.copy()
            params_minus[i] -= delta
            e_minus, _ = self._recompute_energy_from_params(params_minus)

            grad[i] = (e_plus - e_minus) / (2 * delta)

        return grad

    def energy_hessian(self, state: QCState, delta: float = 1e-5) -> np.ndarray:
        """
        Computes the Hessian matrix of the energy function at a given state.

        The Hessian provides information about the local curvature of the energy
        landscape. It's used in more advanced optimization methods (like
        Newton's method) and for stability analysis.

        Args:
            state: The QCState at which to compute the Hessian.
            delta: The perturbation size for finite differences.

        Returns:
            A numpy array representing the Hessian matrix.
        """
        # Similar to the gradient, this is a simplified finite-difference calculation.
        params = np.array([
            state.energy_components.static,
            state.energy_components.dynamic,
            state.energy_components.interaction
        ])
        n = len(params)
        hessian = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                # Central difference for second derivatives
                params_pp = params.copy(); params_pp[i] += delta; params_pp[j] += delta
                e_pp, _ = self._recompute_energy_from_params(params_pp)

                params_pm = params.copy(); params_pm[i] += delta; params_pm[j] -= delta
                e_pm, _ = self._recompute_energy_from_params(params_pm)

                params_mp = params.copy(); params_mp[i] -= delta; params_mp[j] += delta
                e_mp, _ = self._recompute_energy_from_params(params_mp)

                params_mm = params.copy(); params_mm[i] -= delta; params_mm[j] -= delta
                e_mm, _ = self._recompute_energy_from_params(params_mm)

                hessian[i, j] = (e_pp - e_pm - e_mp + e_mm) / (4 * delta**2)

        return hessian

    def _recompute_energy_from_params(self, params: np.ndarray) -> Tuple[float, EnergyComponents]:
        """
        A helper method to mock energy re-computation from perturbed parameters.
        In a real system, this would involve a complex process of altering the
        system's configuration or code, and re-running metric analysis.
        """
        components = EnergyComponents(static=params[0], dynamic=params[1], interaction=params[2])
        return components.total, components

    def check_stability_with_lyapunov(self, state: QCState) -> bool:
        """
        Integrates with Lyapunov functions to check for system stability.

        A negative definite Lyapunov function derivative w.r.t. time indicates stability.
        Here we use the energy gradient as a proxy for the system's dynamics.

        Args:
            state: The current system state.

        Returns:
            True if the system is stable at this state, False otherwise.
        """
        # The Lyapunov function V(x) can be the energy function itself.
        # The time derivative dV/dt = (dV/dx) * (dx/dt).
        # We model dx/dt as being proportional to -grad(V), i.e., gradient descent.
        # So, dV/dt = grad(V) . (-grad(V)) = -||grad(V)||^2, which is <= 0.
        # The system is stable if the gradient is non-zero.

        grad = self.energy_gradient(state)
        # Using a simplified check based on the norm of the gradient.
        # If the gradient is zero, we are at a critical point (stable or unstable).
        # A more rigorous check would involve the Hessian's eigenvalues.
        is_stable = np.linalg.norm(grad) > 1e-6
        return is_stable

    def get_annealing_schedule(self, initial_temp: float, min_temp: float,
                               cooling_rate: float) -> annealing.TemperatureSchedule:
        """
        Creates a temperature schedule for simulated annealing.

        Args:
            initial_temp: The starting temperature.
            min_temp: The minimum temperature to stop at.
            cooling_rate: The rate of cooling (e.g., 0.99 for geometric cooling).

        Returns:
            An instance of a TemperatureSchedule.
        """
        return annealing.GeometricCoolingSchedule(
            initial_temp=initial_temp,
            cooling_rate=cooling_rate,
            min_temp=min_temp
        )
