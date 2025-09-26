"""
Centralized Mathematical Engine for QuantaCirc.

This module provides a unified interface to all the mathematical utilities
required by the system. It acts as a facade, decoupling the core logic
from the specific mathematical implementations.
"""

from __future__ import annotations

from typing import Dict, Any

import math
from scipy.stats import norm
from math_utils.info_entropy import shannon_entropy, kolmogorov_approx
from math_utils.pl_inequality import verify_pl_inequality
from math_utils.lyapunov import calculate_lyapunov_potential
from math_utils.uncertainty_bounds import hoeffding_inequality
from math_utils.annealing import TemperatureSchedule
from core.energy_calculator import EnergyCalculator
from .types import QCState


class MathEngine:
    """
    The central mathematical engine of the QuantaCirc system.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the MathEngine with the necessary configurations.

        Args:
            config: A dictionary containing configuration parameters for
                    the various mathematical components.
        """
        self.config = config
        self.energy_calculator = EnergyCalculator(**config.get('energy', {}))
        self.lyapunov_config = config.get('lyapunov', {})

    def compute_system_energy(self, state: QCState) -> tuple[float, dict[str, float]]:
        """
        Computes the total energy of the system and its components.
        """
        return self.energy_calculator.calculate_energy(state)

    def compute_lyapunov_potential(self, state: QCState) -> float:
        """
        Computes the Lyapunov potential of the system.
        """
        return calculate_lyapunov_potential(
            energy=state.energy,
            num_failing_tests=state.failing_tests,
            num_open_obligations=state.open_obligations,
            kappa=self.lyapunov_config.get('kappa', 10.0),
            xi=self.lyapunov_config.get('xi', 5.0)
        )

    def get_failure_probability_bound(
        self,
        num_tests: int,
        num_failures: int,
        confidence: float = 0.95
    ) -> float:
        """
        Calculates an upper bound on the true failure probability using the
        Wilson score interval.

        Args:
            num_tests (int): The total number of empirical tests run.
            num_failures (int): The number of observed failures.
            confidence (float): The desired confidence level (e.g., 0.95).

        Returns:
            A conservative upper bound for the true failure probability.
        """
        if num_tests == 0:
            return 1.0

        p_hat = num_failures / num_tests
        z = norm.ppf(1 - (1 - confidence) / 2)

        numerator = p_hat + (z**2 / (2 * num_tests)) + z * math.sqrt((p_hat * (1 - p_hat) / num_tests) + (z**2 / (4 * num_tests**2)))
        denominator = 1 + (z**2 / num_tests)

        upper_bound = numerator / denominator
        return min(1.0, upper_bound)

    def __repr__(self) -> str:
        return f"MathEngine(config={self.config})"

    def compute_gradient(self, state: QCState) -> Dict[str, float]:
        """
        Computes the gradient of the energy function.
        """
        return self.energy_calculator.compute_gradient(state)

    def gradient_norm(self, gradient: Dict[str, float]) -> float:
        """
        Computes the norm of the gradient.
        """
        return self.energy_calculator.gradient_norm(gradient)