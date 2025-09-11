"""
Energy Calculator
"""
from typing import Tuple, Dict

class EnergyCalculator:
    def __init__(self, alpha: float, beta: float, gamma: float, delta: float, w_code_quality: float = 1.0, w_uncertainty: float = 10.0, w_performance: float = 100.0, w_replicas: float = 1.0, w_data_flow_efficiency: float = 1.0, stability_threshold: float = 50.0, w_vulnerability_fix: float = 20.0):
        if not all(w >= 0 for w in [alpha, beta, gamma, delta, w_code_quality, w_uncertainty, w_performance, w_replicas, w_data_flow_efficiency, stability_threshold, w_vulnerability_fix]):
            raise ValueError("Energy weights must be non-negative.")
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.w_code_quality = w_code_quality
        self.w_uncertainty = w_uncertainty
        self.w_performance = w_performance
        self.w_replicas = w_replicas
        self.w_data_flow_efficiency = w_data_flow_efficiency
        self.stability_threshold = stability_threshold
        self.w_vulnerability_fix = w_vulnerability_fix
        self.config = {
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
            "delta": delta,
            "w_code_quality": w_code_quality,
            "w_uncertainty": w_uncertainty,
            "w_performance": w_performance,
            "w_replicas": w_replicas,
            "w_data_flow_efficiency": w_data_flow_efficiency,
            "stability_threshold": stability_threshold,
            "w_vulnerability_fix": w_vulnerability_fix,
        }

    def calculate_energy(self, state) -> Tuple[float, Dict[str, float]]:
        components = {
            "complexity": state.complexity,
            "coupling": state.coupling,
            "constraints": state.constraints,
            "debt": state.debt,
        }
        total_energy = (
            self.alpha * components["complexity"]
            + self.beta * components["coupling"]
            + self.gamma * components["constraints"]
            + self.delta * components["debt"]
        )
        return total_energy, components

    def compute_gradient(self, state) -> Dict[str, float]:
        # This is a simplified gradient calculation.
        # A real implementation would involve more complex partial derivatives.
        return {
            "complexity": self.alpha,
            "coupling": self.beta,
            "constraint": self.gamma,
            "debt": self.delta,
        }

    def gradient_norm(self, gradient: Dict[str, float]) -> float:
        return sum(v**2 for v in gradient.values())**0.5

    def descent_direction(self, gradient: Dict[str, float]) -> Dict[str, float]:
        return {k: -v for k, v in gradient.items()}

    def compute_static_energy(self, static_metrics: Dict[str, float]) -> float:
        """
        Computes the static energy component based on metrics that do not
        require a full state simulation (e.g., complexity, coupling).
        """
        complexity = static_metrics.get('cyclomatic_complexity', 0.0)
        coupling = static_metrics.get('coupling', 0.0)

        # Static energy only considers complexity and coupling components.
        static_energy = (
            self.alpha * complexity
            + self.beta * coupling
        )
        return static_energy
