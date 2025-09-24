import math
from typing import List, Tuple
from core.types import SystemState, GrowthPredictionInstance, ScalingRecommendation

class ViscousSpreading:
    def __init__(self):
        pass

    def measure_effective_viscosity(self, state: SystemState) -> float:
        """Measures the system's resistance to change (effective viscosity)."""
        if state.module_count == 0 or state.team_size == 0:
            return float('inf')
        complexity_resistance = state.total_complexity / state.module_count
        coupling_resistance = state.coupling_density**2
        team_resistance = 1.0 / (state.team_size**0.5)
        return complexity_resistance + coupling_resistance + team_resistance

    def radius_to_system_size(self, r: float) -> float:
        """Heuristic: system size grows with area of the spread."""
        return math.pi * r**2 if r != float('inf') else float('inf')

    def radius_to_complexity(self, r: float) -> float:
        """Heuristic: complexity grows with volume of the spread."""
        return (4/3) * math.pi * r**3 if r != float('inf') else float('inf')

    def compute_confidence_interval(self, r: float, t: float) -> Tuple[float, float]:
        """Uncertainty grows with sqrt(t)."""
        if r == float('inf'): return (float('inf'), float('inf'))
        margin = 0.1 * r * math.sqrt(t) if t > 0 else 0
        return (r - margin, r + margin)

    def generate_scaling_recommendations(self, predictions: List[GrowthPredictionInstance]) -> List[ScalingRecommendation]:
        """Generates recommendations based on complexity growth rate."""
        if len(predictions) < 2: return []

        t_i, size_i, comp_i = predictions[0].time, predictions[0].predicted_size, predictions[0].predicted_complexity
        t_f, size_f, comp_f = predictions[-1].time, predictions[-1].predicted_size, predictions[-1].predicted_complexity

        if (t_f - t_i) == 0: return []
        growth_rate = (comp_f - comp_i) / (t_f - t_i)

        if growth_rate > 1000:
            return [ScalingRecommendation(recommendation="High complexity growth rate detected. Recommend major architectural review.")]
        elif growth_rate > 200:
            return [ScalingRecommendation(recommendation="Moderate complexity growth. Recommend investing in CI/CD.")]
        return []

    def assess_sustainability(self, predictions: List[GrowthPredictionInstance]) -> float:
        """Assesses sustainability by comparing complexity growth to size growth."""
        if len(predictions) < 2: return 1.0

        size_i, comp_i = predictions[0].predicted_size, predictions[0].predicted_complexity
        size_f, comp_f = predictions[-1].predicted_size, predictions[-1].predicted_complexity

        if size_i == 0 or comp_i == 0: return 0.0
        size_growth = (size_f - size_i) / size_i
        comp_growth = (comp_f - comp_i) / comp_i

        if size_growth <= 0: return 1.0 if comp_growth <= 0 else 0.0
        ratio = comp_growth / size_growth
        return 1.0 / (1.0 + ratio)
