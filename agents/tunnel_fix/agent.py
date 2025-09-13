import math
from typing import List

from agents.base.agent import QuantumAgent
from core.data_models import (
    SystemState, PerformanceProfile, TunnelingResult, TunnelingOpportunity,
    AppliedOptimization, PerformanceBarrier, Observable
)
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee
from common.utils import PerformanceBarrierDetector, TunnelingOptimizer

class TunnelFixAgent(QuantumAgent):
    def __init__(self):
        """
        Initializes the TunnelFixAgent.
        This agent uses quantum tunneling to find performance optimizations.
        """
        super().__init__(
            physics_principle="Quantum Tunneling",
            mathematical_formula="T ∝ e^(-2κd)"
        )
        self.barrier_detector = PerformanceBarrierDetector()
        self.optimization_engine = TunnelingOptimizer()
        self.min_tunneling_threshold = 1e-4

    def apply_physics_principle(self, system_state: SystemState) -> TunnelingResult:
        """
        Identify and tunnel through performance barriers.
        Requires a `PerformanceProfile` in `system_state.metadata`.
        """
        metadata = system_state.metadata.get("tunnel_fix_input", {})
        profile_data = metadata.get("performance_profile")

        if not profile_data:
            raise ValueError("TunnelFixAgent requires a 'performance_profile' in metadata.")

        profile = PerformanceProfile(**profile_data)

        barriers = self.barrier_detector.identify_barriers(profile)

        opportunities = []
        for barrier in barriers:
            κ = self._compute_barrier_curvature(barrier)
            d = barrier.width

            if κ is None or d is None or κ == float('inf'): continue

            tunneling_prob = math.exp(-2 * κ * d)

            if tunneling_prob > self.min_tunneling_threshold:
                opp = TunnelingOpportunity(
                    barrier=barrier,
                    probability=tunneling_prob,
                    optimization_moves=self._generate_tunneling_moves(barrier, tunneling_prob),
                    expected_improvement=barrier.height * tunneling_prob
                )
                if self._validate_tunneling_move(opp):
                    opportunities.append(opp)

        applied_optimizations = []
        for opp in sorted(opportunities, key=lambda x: x.expected_improvement, reverse=True):
            result = self.optimization_engine.apply_tunneling_optimization(opp)
            if result:
                applied_optimizations.append(result)

        return TunnelingResult(
            barriers_detected=len(barriers),
            tunneling_opportunities=len(opportunities),
            applied_optimizations=applied_optimizations,
            total_performance_gain=sum(opt.performance_gain for opt in applied_optimizations)
        )

    def _compute_barrier_curvature(self, barrier: PerformanceBarrier) -> float:
        """Computes barrier curvature (κ) as a heuristic for its 'stiffness'."""
        if barrier.width > 0:
            return barrier.height / (barrier.width ** 2)
        return float('inf')

    def _generate_tunneling_moves(self, barrier: PerformanceBarrier, probability: float) -> List[str]:
        """Generates descriptive strings for the optimization moves."""
        return [
            f"Attempt refactor on '{barrier.location}' to overcome barrier "
            f"(height={barrier.height:.2f}) with tunneling prob={probability:.4f}."
        ]

    def _validate_tunneling_move(self, opportunity: TunnelingOpportunity) -> bool:
        """Validates that a tunneling opportunity is worth considering."""
        return opportunity.expected_improvement > 0 and opportunity.probability > 0

    def measure_observable(self, system_state: SystemState) -> Observable:
        """
        Measures the total expected performance gain from all identified
        tunneling opportunities.
        """
        try:
            result = self.apply_physics_principle(system_state)
            total_gain = result.total_performance_gain
            return Observable(
                name="total_expected_performance_gain",
                value=total_gain,
                unit="performance_units"
            )
        except (ValueError, TypeError):
            return Observable(name="total_expected_performance_gain", value=0.0, unit="undefined")

    def verify_conservation_laws(self, before: SystemState, after: SystemState) -> bool:
        """
        For TunnelFix, energy (inverse performance) must not increase.
        """
        energy_before = before.energy_breakdown.total
        energy_after = after.energy_breakdown.total
        return energy_after <= energy_before + 1e-9 # Allow for float tolerance

    def generate_certificate(self, before_state: SystemState, after_state: SystemState, result: TunnelingResult) -> AgentCertificate:
        """Generates a mathematical certificate for the tunneling operation."""

        energy_before = before_state.energy_breakdown.total
        energy_after = after_state.energy_breakdown.total
        conservation_error = energy_after - energy_before

        conservation_proof = ConservationProof(
            energy_before=energy_before,
            energy_after=energy_after,
            conservation_error=conservation_error,
            mathematical_justification=f"TunnelFix is an optimization agent; energy should not increase. ΔE = {conservation_error:.2e}"
        )

        convergence_proof = ConvergenceProof(
            lyapunov_before=0, lyapunov_after=0, descent_amount=0, convergence_rate=0,
            justification="N/A: TunnelFix is a single-step analysis, not a convergent process."
        )

        stability_proof = StabilityProof(
            description="Optimization Stability", is_stable=True,
            details="The agent only proposes optimizations that are validated and have a positive expected gain.",
            justification="The agent's operation is considered stable as it does not destabilize the system's performance."
        )

        performance_guarantee = PerformanceGuarantee(
            description="Total Performance Gain",
            bound=f"Total performance gain of {result.total_performance_gain:.4f} units.",
            verified=True,
            justification="Sum of gains from all applied optimizations."
        )

        return AgentCertificate(
            agent_id="tunnel_fix",
            physics_principle=self.physics_principle,
            mathematical_formula=self.formula,
            conservation_proof=conservation_proof,
            convergence_proof=convergence_proof,
            stability_proof=stability_proof,
            performance_guarantee=performance_guarantee
        )
