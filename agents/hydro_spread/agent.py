import math
import numpy as np
from typing import List, Tuple

from common.base_agent import PhysicsBasedAgent
from common.data_models import (
    SystemState, GrowthParameters, GrowthPrediction, GrowthPredictionInstance,
    ScalingRecommendation, Observable
)
from common.utils import HydrodynamicGrowthModeler

class HydroSpreadAgent(PhysicsBasedAgent):
    def __init__(self):
        super().__init__(
            physics_principle="Viscous Spreading",
            mathematical_formula="R(t) = (5ρg/3πμ)^(1/8)V^(3/8)t^(1/8)"
        )
        self.growth_modeler = HydrodynamicGrowthModeler()

    def apply_physics_principle(self, current_state: SystemState, growth_parameters: GrowthParameters, **kwargs) -> GrowthPrediction:
        """Predict system growth using viscous spreading model"""
        ρ = growth_parameters.density
        g = growth_parameters.gravity
        μ = self._measure_effective_viscosity(current_state)
        V = current_state.current_volume

        if μ <= 0:
            raise ValueError("Viscosity must be positive.")

        C = (5 * ρ * g / (3 * math.pi * μ)) ** (1/8)

        predictions = []
        for t in growth_parameters.time_horizons:
            if t < 0: continue
            # Handle t=0 case to avoid 0^(1/8) issues if they arise, though it's usually 0.
            predicted_radius = C * (V ** (3/8)) * (t ** (1/8)) if t > 0 else 0

            predicted_size = self._radius_to_system_size(predicted_radius)
            predicted_complexity = self._radius_to_complexity(predicted_radius)

            predictions.append(GrowthPredictionInstance(
                time=t,
                predicted_radius=predicted_radius,
                predicted_size=predicted_size,
                predicted_complexity=predicted_complexity,
                confidence_interval=self._compute_confidence_interval(predicted_radius, t)
            ))

        scaling_recommendations = self._generate_scaling_recommendations(predictions)

        return GrowthPrediction(
            predictions=predictions,
            viscosity=μ,
            spreading_coefficient=C,
            scaling_recommendations=scaling_recommendations,
            growth_sustainability=self._assess_sustainability(predictions)
        )

    def _measure_effective_viscosity(self, state: SystemState) -> float:
        """Measure system's resistance to change (effective viscosity)"""
        if state.module_count == 0 or state.team_size == 0:
            return float('inf') # Avoid division by zero

        complexity_resistance = state.total_complexity / state.module_count
        coupling_resistance = state.coupling_density ** 2
        team_resistance = 1.0 / (state.team_size ** 0.5)

        return complexity_resistance + coupling_resistance + team_resistance

    def _radius_to_system_size(self, radius: float) -> float:
        """Placeholder to convert growth radius to system size (e.g., lines of code)."""
        return 1000 * (radius**2)

    def _radius_to_complexity(self, radius: float) -> float:
        """Placeholder to convert growth radius to system complexity."""
        return 10 * (radius**3)

    def _compute_confidence_interval(self, predicted_radius: float, t: float) -> Tuple[float, float]:
        """Placeholder to compute a confidence interval for the prediction."""
        error_margin = predicted_radius * 0.1 * (t**0.5)
        return (max(0, predicted_radius - error_margin), predicted_radius + error_margin)

    def _generate_scaling_recommendations(self, predictions: List[GrowthPredictionInstance]) -> List[ScalingRecommendation]:
        """Placeholder to generate scaling recommendations."""
        if not predictions: return []
        last_prediction = predictions[-1]
        if last_prediction.predicted_complexity > 1000:
            return [ScalingRecommendation(recommendation="High complexity predicted. Consider refactoring.")]
        return [ScalingRecommendation(recommendation="Projected growth appears manageable.")]

    def _assess_sustainability(self, predictions: List[GrowthPredictionInstance]) -> float:
        """Placeholder to assess growth sustainability."""
        if not predictions or len(predictions) < 2: return 1.0

        start_complexity = predictions[0].predicted_complexity
        end_complexity = predictions[-1].predicted_complexity
        time_delta = predictions[-1].time - predictions[0].time

        if time_delta < 1e-6: return 1.0

        growth_rate = (end_complexity - start_complexity) / time_delta
        return max(0, 1.0 - growth_rate / 1000.0)

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measure the system's effective viscosity."""
        viscosity = self._measure_effective_viscosity(system_state)
        return Observable(
            name="effective_viscosity",
            value=viscosity,
            unit="viscosity_units"
        )
