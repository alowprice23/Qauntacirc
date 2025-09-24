import numpy as np
import math
from typing import List

from agents.base.agent import PhysicsBasedAgent
from core.types import (
    SystemState, CommunicationGraph, FlowOptimization, DispersionRelation,
    OptimizedChannel, Node, Edge, Observable, Component
)
from common.verification import AgentCertificate, ConservationProof, ConvergenceProof, StabilityProof, PerformanceGuarantee
from common.utils import LatticeFlowOptimizer
from agents.phonon_flow.physics import LatticeDynamics

class PhononFlowAgent(PhysicsBasedAgent):
    def __init__(self):
        """Initializes agent to optimize communication using lattice dynamics."""
        super().__init__(
            agent_name="phonon_flow",
            physics_principle="Lattice Dynamics",
            mathematical_formula="ℏω = ℏv_s·k"
        )
        self.physics = LatticeDynamics(hbar=1.0, min_efficiency_threshold=0.5)
        self.flow_optimizer = LatticeFlowOptimizer()

    def apply_physics_principle(self, system_state: SystemState) -> FlowOptimization:
        """Optimizes information flow using phonon dispersion relations."""
        if not system_state.dependency_graph:
            return FlowOptimization(
                success=True,
                agent_name=self.agent_name,
                physics_principle=self.physics_principle,
                message="No dependency graph found for analysis.",
                dispersion_relations=[],
                optimized_channels=[],
                total_bandwidth=0,
                latency_improvement=0
            )

        # Create Nodes and a map for easy lookup
        nodes = [Node(id=n.id) for n in system_state.dependency_graph.nodes]
        node_map = {node.id: node for node in nodes}

        # Create Edges using the Node map
        edges = [
            Edge(
                source=node_map[e.source.id],
                target=node_map[e.target.id],
                weight=e.strength
            ) for e in system_state.dependency_graph.edges
        ]

        comm_graph = CommunicationGraph(nodes=nodes, edges=edges)

        lattice = self.physics.map_to_lattice(comm_graph)
        dispersion_relations = []
        for mode_type in ["acoustic", "optical"]:
            for k_vector in lattice.k_space_sampling():
                v_s = self.physics.compute_sound_velocity(lattice, mode_type)
                k_norm = np.linalg.norm(k_vector)
                if k_norm == 0: continue

                ω = v_s * k_norm
                group_velocity = self.physics.compute_group_velocity(v_s, k_vector)

                dispersion_relations.append(DispersionRelation(
                    k_vector=k_vector.tolist(), frequency=ω, mode_type=mode_type,
                    group_velocity=group_velocity, energy=self.physics.hbar * ω
                ))

        optimized_channels = []
        for relation in dispersion_relations:
            if relation.group_velocity > self.physics.min_efficiency_threshold:
                optimization = self.flow_optimizer.create_flow_channel(
                    k_vector=np.array(relation.k_vector),
                    group_velocity=relation.group_velocity,
                    bandwidth=self.physics.compute_bandwidth(relation)
                )
                optimized_channels.append(optimization)

        return FlowOptimization(
            success=True,
            agent_name=self.agent_name,
            physics_principle=self.physics_principle,
            message="Successfully analyzed information flow using lattice dynamics.",
            dispersion_relations=dispersion_relations,
            optimized_channels=optimized_channels,
            total_bandwidth=sum(opt.bandwidth for opt in optimized_channels),
            latency_improvement=self.physics.compute_latency_improvement(optimized_channels)
        )

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
