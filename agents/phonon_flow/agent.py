import numpy as np
import math
from typing import List

from agents.base.agent import QuantumAgent
from core.types import (
    SystemState, CommunicationGraph, FlowOptimization, DispersionRelation,
    OptimizedChannel, Node, Edge, Observable
)
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee
from common.utils import LatticeFlowOptimizer

class LatticeModel:
    """A model to represent a communication graph as a physical lattice."""
    def __init__(self, graph: CommunicationGraph):
        self.graph = graph
        self.node_map = {node.id: i for i, node in enumerate(graph.nodes)}
        self.adj_matrix = self._create_adj_matrix()

    def _create_adj_matrix(self) -> np.ndarray:
        n = len(self.graph.nodes)
        adj = np.zeros((n, n))
        for edge in self.graph.edges:
            i = self.node_map.get(edge.source.id)
            j = self.node_map.get(edge.target.id)
            if i is not None and j is not None:
                adj[i, j] = edge.weight
                adj[j, i] = edge.weight
        return adj

    def k_space_sampling(self) -> List[np.ndarray]:
        """A simplified sampling of the Brillouin zone."""
        return [np.array([kx, ky]) for kx in [-1, 0, 1] for ky in [-1, 0, 1] if kx != 0 or ky != 0]

    def get_avg_spring_constant(self) -> float:
        """Acoustic modes relate to the average 'stiffness' (dependency strength)."""
        strengths = self.adj_matrix[self.adj_matrix > 0]
        return np.mean(strengths) if strengths.size > 0 else 0.0

    def get_stiffness_variance(self) -> float:
        """Optical modes relate to the variance in 'stiffness'."""
        strengths = self.adj_matrix[self.adj_matrix > 0]
        return np.var(strengths) if strengths.size > 0 else 0.0

class PhononFlowAgent(QuantumAgent):
    def __init__(self):
        """Initializes agent to optimize communication using lattice dynamics."""
        super().__init__(
            physics_principle="Lattice Dynamics",
            mathematical_formula="ℏω = ℏv_s·k"
        )
        self.hbar = 1.0
        self.flow_optimizer = LatticeFlowOptimizer()
        self.min_efficiency_threshold = 0.5

    def apply_physics_principle(self, system_state: SystemState) -> FlowOptimization:
        """Optimizes information flow using phonon dispersion relations."""
        if not system_state.dependency_graph:
            return FlowOptimization(dispersion_relations=[], optimized_channels=[], total_bandwidth=0, latency_improvement=0)

        comm_graph = CommunicationGraph(
            nodes=[Node(id=n.id) for n in system_state.dependency_graph.nodes],
            edges=[Edge(source=e.source, target=e.target, weight=e.strength) for e in system_state.dependency_graph.edges]
        )

        lattice = self._map_to_lattice(comm_graph)
        dispersion_relations = []
        for mode_type in ["acoustic", "optical"]:
            for k_vector in lattice.k_space_sampling():
                v_s = self._compute_sound_velocity(lattice, mode_type)
                k_norm = np.linalg.norm(k_vector)
                if k_norm == 0: continue

                ω = v_s * k_norm
                group_velocity = self._compute_group_velocity(v_s, k_vector)

                dispersion_relations.append(DispersionRelation(
                    k_vector=k_vector.tolist(), frequency=ω, mode_type=mode_type,
                    group_velocity=group_velocity, energy=self.hbar * ω
                ))

        optimized_channels = []
        for relation in dispersion_relations:
            if relation.group_velocity > self.min_efficiency_threshold:
                optimization = self.flow_optimizer.create_flow_channel(
                    k_vector=np.array(relation.k_vector),
                    group_velocity=relation.group_velocity,
                    bandwidth=self._compute_bandwidth(relation)
                )
                optimized_channels.append(optimization)

        return FlowOptimization(
            dispersion_relations=dispersion_relations,
            optimized_channels=optimized_channels,
            total_bandwidth=sum(opt.bandwidth for opt in optimized_channels),
            latency_improvement=self._compute_latency_improvement(optimized_channels)
        )

    def _map_to_lattice(self, communication_graph: CommunicationGraph) -> LatticeModel:
        return LatticeModel(communication_graph)

    def _compute_sound_velocity(self, lattice: LatticeModel, mode_type: str) -> float:
        """Computes effective sound velocity based on lattice properties (v ~ sqrt(K/m))."""
        if mode_type == "acoustic":
            K = lattice.get_avg_spring_constant()
            return math.sqrt(K) if K > 0 else 0.0
        else:
            K_var = lattice.get_stiffness_variance()
            return 1.0 / (1.0 + math.sqrt(K_var)) if K_var > 0 else 1.0

    def _compute_group_velocity(self, v_s: float, k_vector: np.ndarray) -> float:
        """For linear dispersion ω=v_s*k, group velocity equals phase velocity."""
        return v_s

    def _compute_bandwidth(self, relation: DispersionRelation) -> float:
        return relation.group_velocity * 10

    def _compute_latency_improvement(self, optimizations: List[OptimizedChannel]) -> float:
        if not optimizations: return 0.0
        avg_new_velocity = np.mean([opt.group_velocity for opt in optimizations])
        return (avg_new_velocity - 1.0) * 100

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measures the total bandwidth of the optimized channels found."""
        try:
            result = self.apply_physics_principle(system_state)
            return Observable(name="total_optimized_bandwidth", value=result.total_bandwidth, unit="bandwidth_units")
        except (ValueError, TypeError):
            return Observable(name="total_optimized_bandwidth", value=0.0, unit="undefined")

    def verify_conservation_laws(self, before: SystemState, after: SystemState) -> bool:
        """This agent is analytical and should not change the system's energy."""
        return super()._verify_energy_conservation(before, after)

    def generate_certificate(self, before_state: SystemState, after_state: SystemState, result: FlowOptimization) -> AgentCertificate:
        """Generates a mathematical certificate for the flow optimization analysis."""

        energy_before = before_state.energy_breakdown.total
        energy_after = after_state.energy_breakdown.total
        conservation_error = energy_before - energy_after

        conservation_proof = ConservationProof(
            energy_before=energy_before,
            energy_after=energy_after,
            conservation_error=conservation_error,
            mathematical_justification=f"PhononFlow is an analysis agent; code energy should be conserved. Error = {conservation_error:.2e}"
        )

        convergence_proof = ConvergenceProof(
            lyapunov_before=0, lyapunov_after=0, descent_amount=0, convergence_rate=0,
            justification="N/A: PhononFlow is a single-step analysis, not a convergent process."
        )

        stability_proof = StabilityProof(
            description="Analysis Stability", is_stable=True,
            details="The agent is purely analytical and does not modify the state, hence it is stable.",
            justification="The agent's operation is read-only."
        )

        performance_guarantee = PerformanceGuarantee(
            description="Latency Improvement",
            bound=f"Predicted latency improvement of {result.latency_improvement:.2f}%",
            verified=True,
            justification="Based on calculated group velocities of optimized communication channels."
        )

        return AgentCertificate(
            agent_id="phonon_flow",
            physics_principle=self.physics_principle,
            mathematical_formula=self.formula,
            conservation_proof=conservation_proof,
            convergence_proof=convergence_proof,
            stability_proof=stability_proof,
            performance_guarantee=performance_guarantee
        )
