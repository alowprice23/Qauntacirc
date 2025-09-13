import math
from typing import List, Tuple

from agents.base.agent import QuantumAgent
from core.types import (
    SystemState, GrowthParameters, GrowthPrediction, GrowthPredictionInstance,
    ScalingRecommendation, Observable
)
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee

class HydroSpreadAgent(QuantumAgent):
    def __init__(self):
        """
        Initializes agent to model system growth using viscous spreading.
        """
        super().__init__(
            physics_principle="Viscous Spreading",
            mathematical_formula="R(t) = (5ρg/3πμ)^(1/8)V^(3/8)t^(1/8)"
        )

    def apply_physics_principle(self, system_state: SystemState) -> GrowthPrediction:
        """
        Predict system growth using the viscous spreading model.
        Requires `GrowthParameters` in metadata.
        """
        metadata = system_state.metadata.get("hydro_spread_input", {})
        growth_params_data = metadata.get("growth_parameters")

        if not growth_params_data:
            raise ValueError("HydroSpreadAgent requires 'growth_parameters' in metadata.")

        growth_params = GrowthParameters(**growth_params_data)

        ρ = growth_params.density
        g = growth_params.gravity
        μ = self._measure_effective_viscosity(system_state)
        V = system_state.current_volume

        C = ((5 * ρ * g) / (3 * math.pi * μ))**(1/8) if μ > 0 else float('inf')

        predictions = []
        for t in growth_params.time_horizons:
            predicted_radius = C * (V**(3/8)) * (t**(1/8)) if C != float('inf') else float('inf')
            predictions.append(GrowthPredictionInstance(
                time=t, predicted_radius=predicted_radius,
                predicted_size=self._radius_to_system_size(predicted_radius),
                predicted_complexity=self._radius_to_complexity(predicted_radius),
                confidence_interval=self._compute_confidence_interval(predicted_radius, t)
            ))

        return GrowthPrediction(
            predictions=predictions, viscosity=μ, spreading_coefficient=C,
            scaling_recommendations=self._generate_scaling_recommendations(predictions),
            growth_sustainability=self._assess_sustainability(predictions)
        )

    def _measure_effective_viscosity(self, state: SystemState) -> float:
        """Measures the system's resistance to change (effective viscosity)."""
        if state.module_count == 0 or state.team_size == 0:
            return float('inf')
        complexity_resistance = state.total_complexity / state.module_count
        coupling_resistance = state.coupling_density**2
        team_resistance = 1.0 / (state.team_size**0.5)
        return complexity_resistance + coupling_resistance + team_resistance

    def _radius_to_system_size(self, r: float) -> float:
        """Heuristic: system size grows with area of the spread."""
        return math.pi * r**2 if r != float('inf') else float('inf')

    def _radius_to_complexity(self, r: float) -> float:
        """Heuristic: complexity grows with volume of the spread."""
        return (4/3) * math.pi * r**3 if r != float('inf') else float('inf')

    def _compute_confidence_interval(self, r: float, t: float) -> Tuple[float, float]:
        """Uncertainty grows with sqrt(t)."""
        if r == float('inf'): return (float('inf'), float('inf'))
        margin = 0.1 * r * math.sqrt(t) if t > 0 else 0
        return (r - margin, r + margin)

    def _generate_scaling_recommendations(self, predictions: List[GrowthPredictionInstance]) -> List[ScalingRecommendation]:
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

    def _assess_sustainability(self, predictions: List[GrowthPredictionInstance]) -> float:
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

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measures the effective viscosity (μ) of the system."""
        viscosity = self._measure_effective_viscosity(system_state)
        return Observable(name="effective_viscosity", value=viscosity, unit="resistance_units")

    def verify_conservation_laws(self, before: SystemState, after: SystemState) -> bool:
        """This agent is analytical and should not change the system's energy."""
        return super()._verify_energy_conservation(before, after)

    def generate_certificate(self, before_state: SystemState, after_state: SystemState, result: GrowthPrediction) -> AgentCertificate:
        """Generates a mathematical certificate for the growth prediction analysis."""

        energy_before = before_state.energy_breakdown.total
        energy_after = after_state.energy_breakdown.total
        conservation_error = energy_before - energy_after

        conservation_proof = ConservationProof(
            energy_before=energy_before,
            energy_after=energy_after,
            conservation_error=conservation_error,
            mathematical_justification=f"HydroSpread is an analysis agent; code energy should be conserved. Error = {conservation_error:.2e}"
        )

        convergence_proof = ConvergenceProof(
            lyapunov_before=0, lyapunov_after=0, descent_amount=0, convergence_rate=0,
            justification="N/A: HydroSpread is a single-step analysis, not a convergent process."
        )

        stability_proof = StabilityProof(
            description="Analysis Stability", is_stable=True,
            details="The agent is purely analytical and does not modify the state, hence it is stable.",
            justification="The agent's operation is read-only."
        )

        performance_guarantee = PerformanceGuarantee(
            description="Growth Sustainability Score",
            bound=f"Calculated sustainability score of {result.growth_sustainability:.4f}",
            verified=result.growth_sustainability > 0.5, # Example verification
            justification="Score is based on comparing complexity growth to size growth."
        )

        return AgentCertificate(
            agent_id="hydro_spread",
            physics_principle=self.physics_principle,
            mathematical_formula=self.formula,
            conservation_proof=conservation_proof,
            convergence_proof=convergence_proof,
            stability_proof=stability_proof,
            performance_guarantee=performance_guarantee
        )
