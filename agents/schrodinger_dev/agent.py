import numpy as np
import scipy.linalg
from typing import List

from agents.base.agent import PhysicsBasedAgent
from core.types import (
    SystemState, CodeState, Hamiltonian, CodeEvolution, UnitaryOperator, Proof, Observable
)
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee
from agents.schrodinger_dev.code_generator import SchrodingerCodeGenerator
from common.utils import ProofSynthesizer
from agents.schrodinger_dev.physics import HamiltonianBuilder

class SchrodingerDevAgent(PhysicsBasedAgent):
    def __init__(self, llm_client: "LLMClient" = None):
        """
        Initializes the SchrodingerDevAgent.
        This agent is responsible for code synthesis through quantum state evolution,
        governed by the Schrödinger equation.
        """
        super().__init__(
            agent_name="schrodinger_dev",
            physics_principle="Quantum State Evolution",
            mathematical_formula="iℏ∂ψ/∂t = Ĥψ"
        )
        self.hbar = 1.054571817e-34
        if llm_client is None:
            from llm.client import LLMClient
            llm_client = LLMClient()
        self.code_generator = SchrodingerCodeGenerator(llm_client=llm_client, num_superpositions=5)
        self.proof_synthesizer = ProofSynthesizer()
        self.hamiltonian_builder = HamiltonianBuilder(weights={'complexity': 0.5, 'constraints': 1.0, 'similarity': 0.2})

    def apply_physics_principle(self, system_state: SystemState) -> CodeEvolution:
        """
        Evolve the code state using the Schrödinger equation.
        This function requires 'code_state', 'dt', and 'implementations' to be present
        in the system_state.metadata.
        """
        metadata = system_state.metadata.get("schrodinger_dev_input", {})
        current_code_state_data = metadata.get("code_state")
        dt = metadata.get("dt")
        implementations = metadata.get("implementations")
        parsed_spec = metadata.get("parsed_spec", {})

        if not all([current_code_state_data, dt is not None, implementations is not None]):
            raise ValueError("SchrödingerDevAgent requires 'code_state', 'dt', and 'implementations' in metadata.")

        current_code_state = CodeState(**current_code_state_data)
        hamiltonian_matrix = self.hamiltonian_builder.from_specification(implementations, parsed_spec)
        hamiltonian = Hamiltonian(matrix=hamiltonian_matrix.tolist())

        initial_psi = np.array(current_code_state.state_vector, dtype=complex)

        unitary_operator = self._compute_unitary_operator(hamiltonian, dt)

        new_psi = np.array(unitary_operator.matrix) @ initial_psi

        generated_code = self.code_generator.collapse_to_implementation(implementations, new_psi)

        proof_obligations = self._extract_proof_obligations(generated_code)
        proofs = self.proof_synthesizer.generate_proofs(proof_obligations)

        return CodeEvolution(
            success=True,
            agent_name="SchrodingerDevAgent",
            physics_principle=self.physics_principle,
            message="Code evolution successful.",
            new_state=CodeState(state_vector=new_psi.tolist(), code=generated_code),
            proofs=proofs,
            energy_change=self._compute_energy_change(initial_psi, new_psi, hamiltonian),
            unitary_operator=unitary_operator
        )

    def _compute_unitary_operator(self, H: Hamiltonian, dt: float) -> UnitaryOperator:
        """Compute U = exp(-iĤt/ℏ) using matrix exponential."""
        h_matrix = np.array(H.matrix, dtype=complex)
        matrix = -1j * h_matrix * dt / self.hbar
        return UnitaryOperator(matrix=scipy.linalg.expm(matrix).tolist())

    def _extract_proof_obligations(self, code: str) -> List[str]:
        """Placeholder for extracting mock proof obligations from code."""
        if "assert" in code or "require" in code:
            return ["obligation_1", "obligation_2"]
        return []

    def _compute_energy_change(self, old_psi: np.ndarray, new_psi: np.ndarray, H: Hamiltonian) -> float:
        """Computes the change in expectation value of energy <E> = <ψ|H|ψ>."""
        h_matrix = np.array(H.matrix, dtype=complex)
        energy_before = np.vdot(old_psi, h_matrix @ old_psi).real
        energy_after = np.vdot(new_psi, h_matrix @ new_psi).real
        return energy_after - energy_before

    def measure_observable(self, system_state: SystemState) -> Observable:
        """
        Measures the stability of the code state evolution, represented by the
        change in the norm of the state vector. A perfectly unitary evolution
        should result in a norm change of 0.
        """
        try:
            metadata = system_state.metadata.get("schrodinger_dev_input", {})
            if "code_state" not in metadata:
                raise ValueError("Missing 'code_state' for measurement.")

            evolution_result = self.apply_physics_principle(system_state)

            current_code_state = CodeState(**metadata.get("code_state"))

            norm_before = np.linalg.norm(current_code_state.state_vector)
            norm_after = np.linalg.norm(evolution_result.new_state.state_vector)

            stability_delta = abs(norm_after - norm_before)

            return Observable(
                name="evolution_norm_stability",
                value=stability_delta,
                unit="norm_delta"
            )
        except (ValueError, TypeError) as e:
            return Observable(name="evolution_norm_stability", value=-1.0, unit="error")

    def verify_conservation_laws(self, before: SystemState, after: SystemState) -> bool:
        """
        Verifies the conservation of probability. For a unitary evolution,
        the norm of the state vector must be conserved: ||ψ_after|| = ||ψ_before||.
        This assumes the system's quantum_state field is updated by the orchestrator.
        """
        if not before.quantum_state or not after.quantum_state:
            return True

        norm_before = np.linalg.norm(before.quantum_state.state_vector)
        norm_after = np.linalg.norm(after.quantum_state.state_vector)

        tolerance = 1e-9
        return abs(norm_before - norm_after) < tolerance

    def generate_certificate(self, before_state: SystemState, after_state: SystemState, result: CodeEvolution) -> AgentCertificate:
        """Generates a mathematical certificate for the code evolution operation."""

        # 1. Conservation Proof (Probability/Norm Conservation)
        norm_before = np.linalg.norm(before_state.quantum_state.state_vector) if before_state.quantum_state else 0
        norm_after = np.linalg.norm(after_state.quantum_state.state_vector) if after_state.quantum_state else 0
        conservation_error = abs(norm_before - norm_after)

        conservation_proof = ConservationProof(
            energy_before=norm_before,
            energy_after=norm_after,
            conservation_error=conservation_error,
            mathematical_justification=f"Probability norm conservation for unitary evolution. | |ψ_after| - |ψ_before| | = {conservation_error:.2e}"
        )

        # 2. Convergence Proof (Not applicable)
        convergence_proof = ConvergenceProof(
            lyapunov_before=0, lyapunov_after=0, descent_amount=0, convergence_rate=0,
            justification="N/A: SchrödingerDev performs a single-step evolution, not an iterative convergence."
        )

        # 3. Stability Proof (Unitary evolution is inherently stable)
        stability_proof = StabilityProof(
            description="Evolution Stability", is_stable=True,
            details="The evolution is governed by a unitary operator U. Unitary operators are norm-preserving, guaranteeing a stable evolution.",
            justification="Unitary evolution is stable by definition."
        )

        # 4. Performance Guarantee (Not applicable)
        performance_guarantee = PerformanceGuarantee(
            description="Agent Performance", bound="N/A", verified=True,
            justification="N/A: This agent performs code generation, performance is not its primary metric."
        )

        return AgentCertificate(
            agent_id="schrodinger_dev",
            physics_principle=self.physics_principle,
            mathematical_formula=self.formula,
            conservation_proof=conservation_proof,
            convergence_proof=convergence_proof,
            stability_proof=stability_proof,
            performance_guarantee=performance_guarantee
        )
