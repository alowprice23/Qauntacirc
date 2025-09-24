import numpy as np
import math
from collections import Counter
from typing import List

from agents.base.agent import PhysicsBasedAgent
from core.types import (
    SystemState, UncertaintyAnalysis, Module, Observable, RiskBounds
)
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee
from common.utils import UncertaintyGuidedTestGenerator, RiskQuantifier
from agents.uncertain_ai.physics import UncertaintyPrinciple

class UncertainAIAgent(PhysicsBasedAgent):
    def __init__(self):
        """
        Initializes the UncertainAIAgent.
        This agent applies the Heisenberg Uncertainty Principle to assess risk
        and determine minimum test coverage.
        """
        super().__init__(
            agent_name="uncertain_ai",
            physics_principle="Uncertainty Principle",
            mathematical_formula="Δx·Δp ≥ ℏ/2"
        )
        self.physics = UncertaintyPrinciple(hbar_effective=1.0)
        self.test_generator = UncertaintyGuidedTestGenerator()
        self.risk_quantifier = RiskQuantifier()

    def apply_physics_principle(self, system_state: SystemState) -> UncertaintyAnalysis:
        """
        Apply the uncertainty principle to determine minimum test coverage.
        """
        spec_uncertainty = self.physics.measure_specification_uncertainty(system_state)
        impl_uncertainty = self.physics.measure_implementation_uncertainty(system_state)

        uncertainty_product = spec_uncertainty * impl_uncertainty
        min_uncertainty = self.physics.hbar_effective / 2

        additional_tests = []
        if 0 < uncertainty_product < min_uncertainty:
            required_test_density = min_uncertainty / uncertainty_product
            additional_tests = self.test_generator.generate_tests(system_state, required_test_density)

        risk_bounds_dict = self.risk_quantifier.compute_chernoff_bounds(
            system_state.failing_tests, confidence=0.95
        )
        # The mock in the test returns a dict, but the model expects a RiskBounds object.
        # The production code should handle both dicts and objects.
        if isinstance(risk_bounds_dict, dict):
            risk_bounds = RiskBounds(**risk_bounds_dict)
        else:
            risk_bounds = risk_bounds_dict


        # A system with zero uncertainty perfectly satisfies the principle.
        satisfies = np.isclose(uncertainty_product, 0) or uncertainty_product >= min_uncertainty

        return UncertaintyAnalysis(
            success=True,
            agent_name=self.agent_name,
            physics_principle=self.physics_principle,
            message="Successfully performed uncertainty analysis.",
            spec_uncertainty=spec_uncertainty,
            impl_uncertainty=impl_uncertainty,
            uncertainty_product=uncertainty_product,
            satisfies_principle=satisfies,
            additional_tests=additional_tests,
            risk_bounds=risk_bounds
        )

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measures the uncertainty product (Δx·Δp)."""
        spec_uncertainty = self.physics.measure_specification_uncertainty(system_state)
        impl_uncertainty = self.physics.measure_implementation_uncertainty(system_state)
        uncertainty_product = spec_uncertainty * impl_uncertainty

        return Observable(
            name="uncertainty_product",
            value=uncertainty_product,
            unit="hbar_effective_units"
        )

    def verify_conservation_laws(self, before: SystemState, after: SystemState) -> bool:
        """
        This agent is purely analytical and should not change the system's energy.
        """
        return super()._verify_energy_conservation(before, after)

    def generate_certificate(self, before_state: SystemState, after_state: SystemState, result: UncertaintyAnalysis) -> AgentCertificate:
        """Generates a mathematical certificate for the uncertainty analysis."""

        energy_before = before_state.energy_breakdown.total
        energy_after = after_state.energy_breakdown.total
        conservation_error = energy_before - energy_after

        conservation_proof = ConservationProof(
            energy_before=energy_before,
            energy_after=energy_after,
            conservation_error=conservation_error,
            mathematical_justification=f"UncertainAI is an analysis agent; energy should be conserved. Error = {conservation_error:.2e}"
        )

        convergence_proof = ConvergenceProof(
            lyapunov_before=0, lyapunov_after=0, descent_amount=0, convergence_rate=0,
            justification="N/A: UncertainAI is a single-step analysis, not a convergent process."
        )

        stability_proof = StabilityProof(
            description="Analysis Stability", is_stable=True,
            details="The agent is purely analytical and does not modify the state, hence it is stable.",
            justification="The agent's operation is read-only."
        )

        performance_guarantee = PerformanceGuarantee(
            description="Uncertainty Principle Compliance",
            bound=f"Δx·Δp = {result.uncertainty_product:.4f} >= {self.hbar_effective / 2}",
            verified=result.satisfies_principle,
            justification="Ensures the product of uncertainties meets the minimum threshold."
        )

        return AgentCertificate(
            agent_id="uncertain_ai",
            physics_principle=self.physics_principle,
            mathematical_formula=self.formula,
            conservation_proof=conservation_proof,
            convergence_proof=convergence_proof,
            stability_proof=stability_proof,
            performance_guarantee=performance_guarantee
        )
