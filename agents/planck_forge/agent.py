from agents.base.agent import QuantumAgent
from core.types import SystemState, QuantizedTasks, TaskQuantum, Observable
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee
from llm.client import LLMClient
from .advanced_nl_processor import AdvancedQuantumNLProcessor, SessionContext
from .quantization import EnergyQuantizer

class PlanckForgeAgent(QuantumAgent):
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

        # Initialize the LLM client and the advanced NL processor
        llm_client = LLMClient() # Assuming a default constructor
        self.nl_processor = AdvancedQuantumNLProcessor(llm_client)
        self.energy_quantizer = EnergyQuantizer(planck_constant=self.h)

    async def apply_physics_principle(self, system_state: SystemState) -> QuantizedTasks:
        """
        Convert continuous requirements into discrete task quanta using the advanced NL processor.
        """
        requirements_str = " ".join(system_state.requirements) if system_state.requirements else ""

        if not requirements_str and "planck_forge_input" in system_state.metadata:
             requirements_str = system_state.metadata["planck_forge_input"].get("requirements", "")

        if not requirements_str:
            # Return an empty result if there are no requirements to process
            return QuantizedTasks(quanta=[], total_energy=0.0)

        # Create a session context
        session_context = SessionContext(session_id="placeholder_session", quantum_state=system_state)

        # Process the command using the advanced NL processor
        # Note: This is an async call now
        result = await self.nl_processor.process_complex_multi_step_command(requirements_str, session_context)

        # The result contains TaskQuanta objects. We need to quantize their energy.
        task_quanta_list = self.energy_quantizer.quantize_batch(result.decomposed_operations)

        # Convert TaskQuanta to TaskQuantum
        task_quantum_list = []
        for tq in task_quanta_list:
            task_quantum_list.append(TaskQuantum(
                n=tq.n,
                frequency=tq.frequency,
                energy=tq.energy,
                description=tq.description,
                dependencies=tq.dependencies
            ))

        total_energy = sum(q.energy for q in task_quantum_list)
        return QuantizedTasks(quanta=task_quantum_list, total_energy=total_energy)

    async def measure_observable(self, system_state: SystemState) -> Observable:
        """
        Measure the task quantization efficiency.
        This observable measures how many discrete tasks (quanta) are generated
        per requirement, providing insight into the agent's effectiveness.
        """
        # We must apply the principle to determine the number of quanta generated.
        quantized_tasks_result = await self.apply_physics_principle(system_state)
        num_quanta = len(quantized_tasks_result.quanta)

        # Avoid division by zero if there are no requirements.
        num_requirements = len(system_state.requirements)
        efficiency = num_quanta / num_requirements if num_requirements > 0 else 0.0

        return Observable(
            name="quantization_efficiency",
            value=efficiency,
            unit="quanta_per_requirement"
        )

    async def verify_conservation_laws(self, before: SystemState, after: SystemState) -> bool:
        """
        For PlanckForge, a primary conservation check is that the energy increase
        in the system state corresponds to the energy of the tasks created.
        This check relies on the orchestrator correctly updating the 'after' state.
        """
        # The energy of the newly created tasks
        created_tasks_energy = (await self.apply_physics_principle(before)).total_energy

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
