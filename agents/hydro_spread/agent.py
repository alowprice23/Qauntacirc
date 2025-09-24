import math
from typing import List, Tuple

from agents.base.agent import PhysicsBasedAgent
from core.types import (
    SystemState, GrowthParameters, GrowthPrediction, GrowthPredictionInstance,
    ScalingRecommendation, Observable
)
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee
from agents.hydro_spread.physics import ViscousSpreading

class HydroSpreadAgent(PhysicsBasedAgent):
    def __init__(self):
        """
        Initializes agent to model system growth using viscous spreading.
        """
        super().__init__(
            agent_name="hydro_spread",
            physics_principle="Viscous Spreading",
            mathematical_formula="R(t) = (5ρg/3πμ)^(1/8)V^(3/8)t^(1/8)"
        )
        self.physics = ViscousSpreading()

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
        μ = self.physics.measure_effective_viscosity(system_state)
        V = system_state.current_volume

        C = ((5 * ρ * g) / (3 * math.pi * μ))**(1/8) if μ > 0 else float('inf')

        predictions = []
        for t in growth_params.time_horizons:
            predicted_radius = C * (V**(3/8)) * (t**(1/8)) if C != float('inf') else float('inf')
            predictions.append(GrowthPredictionInstance(
                time=t, predicted_radius=predicted_radius,
                predicted_size=self.physics.radius_to_system_size(predicted_radius),
                predicted_complexity=self.physics.radius_to_complexity(predicted_radius),
                confidence_interval=self.physics.compute_confidence_interval(predicted_radius, t)
            ))

        return GrowthPrediction(
            success=True,
            agent_name=self.agent_name,
            physics_principle=self.physics_principle,
            message="Successfully predicted system growth using viscous spreading model.",
            predictions=predictions,
            viscosity=μ,
            spreading_coefficient=C,
            scaling_recommendations=self.physics.generate_scaling_recommendations(predictions),
            growth_sustainability=self.physics.assess_sustainability(predictions)
        )

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measures the effective viscosity (μ) of the system."""
        viscosity = self.physics.measure_effective_viscosity(system_state)
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
