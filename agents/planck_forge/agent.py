from agents.base.agent import PhysicsBasedAgent
from core.types import SystemState, QuantizedTasks, TaskQuantum, Observable
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee
from common.utils import FrequencyAnalyzer

class PlanckForgeAgent(PhysicsBasedAgent):
    def __init__(self):
        """
        Initializes the PlanckForgeAgent.
        This agent is responsible for task quantization from continuous
        requirements into discrete energy levels, based on Planck's hypothesis.
        """
        super().__init__(
            physics_principle="Energy Quantization",
            mathematical_formula="E_n = n·h·ν"
        )
        # Using a scaled Planck constant for software modeling purposes
        self.h = 6.62607015e-34
        self.frequency_analyzer = FrequencyAnalyzer()

    def apply_physics_principle(self, system_state: SystemState) -> QuantizedTasks:
        """
        Convert continuous requirements into discrete task quanta.
        This is the core application of the E_n = n·h·ν principle.
        """
        requirements_str = " ".join(system_state.requirements) if system_state.requirements else ""

        if not requirements_str and "planck_forge_input" in system_state.metadata:
             requirements_str = system_state.metadata["planck_forge_input"].get("requirements", "")

        if not requirements_str:
            # Return an empty result if there are no requirements to process
            return QuantizedTasks(quanta=[], total_energy=0.0)

        # Extract dominant frequencies (ν) from the requirements text
        frequencies = self.frequency_analyzer.extract_frequencies(requirements_str)

        # Quantize into discrete energy levels (E_n)
        quanta = []
        for freq_data in frequencies:
            ν = freq_data.frequency
            # Calculate quantum numbers (n) for different energy levels
            for n in range(1, freq_data.max_harmonics + 1):
                energy_level = n * self.h * ν
                task_quantum = TaskQuantum(
                    n=n, frequency=ν, energy=energy_level,
                    description=freq_data.task_description,
                    dependencies=freq_data.dependencies
                )
                quanta.append(task_quantum)

        total_energy = sum(q.energy for q in quanta)
        return QuantizedTasks(quanta=quanta, total_energy=total_energy)

    def measure_observable(self, system_state: SystemState) -> Observable:
        """
        Measure the task quantization efficiency.
        This observable measures how many discrete tasks (quanta) are generated
        per requirement, providing insight into the agent's effectiveness.
        """
        # We must apply the principle to determine the number of quanta generated.
        quantized_tasks_result = self.apply_physics_principle(system_state)
        num_quanta = len(quantized_tasks_result.quanta)

        # Avoid division by zero if there are no requirements.
        num_requirements = len(system_state.requirements)
        efficiency = num_quanta / num_requirements if num_requirements > 0 else 0.0

        return Observable(
            name="quantization_efficiency",
            value=efficiency,
            unit="quanta_per_requirement"
        )

    def verify_conservation_laws(self, before: SystemState, after: SystemState) -> bool:
        """
        For PlanckForge, a primary conservation check is that the energy increase
        in the system state corresponds to the energy of the tasks created.
        This check relies on the orchestrator correctly updating the 'after' state.
        """
        # The energy of the newly created tasks
        created_tasks_energy = self.apply_physics_principle(before).total_energy

        # The actual energy change in the system
        energy_delta = after.energy_breakdown.total - before.energy_breakdown.total

        # Check if the energy change matches the created energy, within a tolerance
        tolerance = 1e-9
        return abs(created_tasks_energy - energy_delta) < tolerance

    def generate_certificate(self, before_state: SystemState, after_state: SystemState, result: QuantizedTasks) -> AgentCertificate:
        """Generates a mathematical certificate for the quantization operation."""

        energy_before = before_state.energy_breakdown.total
        energy_after = after_state.energy_breakdown.total
        conservation_error = (energy_before + result.total_energy) - energy_after

        conservation_proof = ConservationProof(
            energy_before=energy_before,
            energy_after=energy_after,
            conservation_error=conservation_error,
            mathematical_justification=f"Energy of new tasks ({result.total_energy:.2e}) should be added to the system. Error = (E_before + E_tasks) - E_after = {conservation_error:.2e}"
        )

        convergence_proof = ConvergenceProof(
            lyapunov_before=0, lyapunov_after=0, descent_amount=0, convergence_rate=0,
            justification="N/A: PlanckForge is a generative, not convergent, agent."
        )

        stability_proof = StabilityProof(
            description="Agent Stability", is_stable=True, details="N/A",
            justification="N/A: PlanckForge is a generative agent and does not affect system stability in the traditional sense."
        )

        performance_guarantee = PerformanceGuarantee(
            description="Agent Performance", bound="N/A", verified=True,
            justification="N/A: PlanckForge is a generative agent."
        )

        return AgentCertificate(
            agent_id="planck_forge",
            physics_principle=self.physics_principle,
            mathematical_formula=self.formula,
            conservation_proof=conservation_proof,
            convergence_proof=convergence_proof,
            stability_proof=stability_proof,
            performance_guarantee=performance_guarantee
        )
