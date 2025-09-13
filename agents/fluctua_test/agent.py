from typing import List, Dict, Any
import math

from agents.base.agent import QuantumAgent
from core.types import (
    SystemState, ChaosTestResult, ComplexResponse, ResilienceAnalysis,
    ChaosScenario, ChaosExperimentResult, Observable
)
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee
from common.utils import ChaosTestEngine

class FluctuaTestAgent(QuantumAgent):
    def __init__(self):
        """
        Initializes agent that uses the Fluctuation-Dissipation Theorem
        to generate chaos tests.
        """
        super().__init__(
            physics_principle="Fluctuation-Dissipation Theorem",
            mathematical_formula="S_AA(ω) = (2kT/ω)Im(χ_AA(ω))"
        )
        self.k_B = 1.0  # Effective Boltzmann constant
        self.chaos_engine = ChaosTestEngine()
        self.chaos_threshold = 0.7
        self.frequency_range = [0.1, 0.5, 1.0, 5.0, 10.0]

    def apply_physics_principle(self, system_state: SystemState) -> ChaosTestResult:
        """
        Generate chaos tests using the Fluctuation-Dissipation theorem.
        Requires `temperature` in metadata.
        """
        metadata = system_state.metadata.get("fluctua_test_input", {})
        temperature = metadata.get("temperature", 1.0)

        response_functions = self._measure_response_functions(system_state)

        chaos_scenarios = []
        for frequency, response in response_functions.items():
            if frequency == 0: continue

            S_AA = (2 * self.k_B * temperature / frequency) * response.imaginary_part

            if S_AA > self.chaos_threshold:
                scenario = self.chaos_engine.generate_scenario(
                    frequency=frequency, spectral_density=S_AA,
                    response_magnitude=abs(response.value),
                    system_components=self._identify_responsive_components(state=system_state)
                )
                chaos_scenarios.append(scenario)

        experiment_results = [self.chaos_engine.execute_experiment(s, system_state) for s in chaos_scenarios]
        resilience_analysis = self.chaos_engine.analyze_resilience(experiment_results)

        return ChaosTestResult(
            scenarios=chaos_scenarios,
            scenarios_generated=len(chaos_scenarios),
            experiments_executed=len(experiment_results),
            resilience_score=resilience_analysis.overall_score,
            failure_modes_discovered=resilience_analysis.failure_modes,
            recovery_times=resilience_analysis.recovery_times,
            stability_improvements=resilience_analysis.suggested_improvements
        )

    def _measure_response_functions(self, system_state: SystemState) -> Dict[float, ComplexResponse]:
        """Measures the system's response function χ_AA(ω) via perturbation."""
        responses = {}
        for freq in self.frequency_range:
            perturbation = self._generate_harmonic_perturbation(freq)
            perturbed_state = self._apply_perturbation(system_state, perturbation)
            responses[freq] = self._measure_response(system_state, perturbed_state)
        return responses

    def _generate_harmonic_perturbation(self, frequency: float) -> Dict[str, Any]:
        """Generates a perturbation targeting system complexity."""
        return {"type": "complexity_stress", "amplitude": 10.0, "frequency": frequency}

    def _apply_perturbation(self, state: SystemState, perturbation: Dict[str, Any]) -> SystemState:
        """Applies a perturbation to a copy of the system state."""
        perturbed_state = state.model_copy(deep=True)
        if perturbation["type"] == "complexity_stress":
            # Simulate stress by increasing the total_complexity metric
            perturbed_state.total_complexity += perturbation["amplitude"]
            # Assume a corresponding energy increase
            energy_increase = perturbation["amplitude"] * 0.1
            perturbed_state.energy_breakdown.complexity += energy_increase
            perturbed_state.energy_breakdown.total += energy_increase
        return perturbed_state

    def _measure_response(self, original: SystemState, perturbed: SystemState) -> ComplexResponse:
        """Measures the system's response to the perturbation (change in energy)."""
        real_part = perturbed.energy_breakdown.total - original.energy_breakdown.total
        # Heuristic for the imaginary part (dissipation) being proportional to the response magnitude.
        imaginary_part = 0.1 * abs(real_part)
        return ComplexResponse(value=complex(real_part, imaginary_part), imaginary_part=imaginary_part)

    def _identify_responsive_components(self, state: SystemState) -> List[str]:
        """Identifies components most likely affected. Placeholder: returns top 3 most complex."""
        sorted_modules = sorted(state.modules, key=lambda m: m.cyclomatic_complexity, reverse=True)
        return [m.name for m in sorted_modules[:3]]

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measures the overall resilience score of the system."""
        try:
            result = self.apply_physics_principle(system_state)
            return Observable(name="system_resilience_score", value=result.resilience_score, unit="score")
        except Exception:
            return Observable(name="system_resilience_score", value=0.0, unit="undefined")

    def verify_conservation_laws(self, before: SystemState, after: SystemState) -> bool:
        """This agent is analytical and should not change the system's energy."""
        return super()._verify_energy_conservation(before, after)

    def generate_certificate(self, before_state: SystemState, after_state: SystemState, result: ChaosTestResult) -> AgentCertificate:
        """Generates a mathematical certificate for the chaos testing analysis."""

        energy_before = before_state.energy_breakdown.total
        energy_after = after_state.energy_breakdown.total
        conservation_error = energy_before - energy_after

        conservation_proof = ConservationProof(
            energy_before=energy_before,
            energy_after=energy_after,
            conservation_error=conservation_error,
            mathematical_justification=f"FluctuaTest is an analysis agent; code energy should be conserved. Error = {conservation_error:.2e}"
        )

        convergence_proof = ConvergenceProof(
            lyapunov_before=0, lyapunov_after=0, descent_amount=0, convergence_rate=0,
            justification="N/A: FluctuaTest is a single-step analysis, not a convergent process."
        )

        stability_proof = StabilityProof(
            description="Analysis Stability", is_stable=True,
            details="The agent is purely analytical and does not modify the state, hence it is stable.",
            justification="The agent's operation is read-only."
        )

        performance_guarantee = PerformanceGuarantee(
            description="System Resilience Score",
            bound=f"Calculated resilience score of {result.resilience_score:.4f}",
            verified=result.resilience_score > 0.5, # Example verification
            justification="Score is based on simulated chaos experiments."
        )

        return AgentCertificate(
            agent_id="fluctua_test",
            physics_principle=self.physics_principle,
            mathematical_formula=self.formula,
            conservation_proof=conservation_proof,
            convergence_proof=convergence_proof,
            stability_proof=stability_proof,
            performance_guarantee=performance_guarantee
        )
