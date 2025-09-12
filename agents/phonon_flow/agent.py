import numpy as np
from typing import List

from common.base_agent import PhysicsBasedAgent
from common.data_models import (
    CommunicationGraph, FlowOptimization, DispersionRelation, Lattice,
    SystemState, Observable, OptimizedChannel, Node
)
from common.utils import LatticeFlowOptimizer

class PhononFlowAgent(PhysicsBasedAgent):
    def __init__(self):
        super().__init__(
            physics_principle="Lattice Dynamics",
            mathematical_formula="ω = v_s·k"
        )
        self.hbar = 1.0  # Effective Planck constant
        self.flow_optimizer = LatticeFlowOptimizer()
        self.min_efficiency_threshold = 0.5 # Corresponds to group velocity

    def apply_physics_principle(self, communication_graph: CommunicationGraph, **kwargs) -> FlowOptimization:
        """Optimize information flow using phonon dispersion relations"""
        lattice = self._map_to_lattice(communication_graph)

        dispersion_relations = []
        for mode_type in ["acoustic", "optical"]:
            for k_vector in lattice.k_space_sampling():
                if np.linalg.norm(k_vector) == 0:
                    continue

                v_s = self._compute_sound_velocity(lattice, mode_type)
                ω = v_s * np.linalg.norm(k_vector)

                dispersion_relations.append(DispersionRelation(
                    k_vector=k_vector,
                    frequency=ω,
                    mode_type=mode_type,
                    group_velocity=self._compute_group_velocity(v_s, k_vector),
                    energy=self.hbar * ω
                ))

        flow_optimizations = []
        for relation in dispersion_relations:
            if relation.group_velocity > self.min_efficiency_threshold:
                optimization = self.flow_optimizer.create_flow_channel(
                    k_vector=relation.k_vector,
                    group_velocity=relation.group_velocity,
                    bandwidth=self._compute_bandwidth(relation.frequency)
                )
                flow_optimizations.append(optimization)

        return FlowOptimization(
            dispersion_relations=dispersion_relations,
            optimized_channels=flow_optimizations,
            total_bandwidth=sum(opt.bandwidth for opt in flow_optimizations),
            latency_improvement=self._compute_latency_improvement(communication_graph, flow_optimizations)
        )

    def _map_to_lattice(self, communication_graph: CommunicationGraph) -> Lattice:
        """Placeholder to map a communication graph to a lattice structure."""
        print(f"Mapping graph with {len(communication_graph.nodes)} nodes to a mock lattice.")
        return Lattice()

    def _compute_sound_velocity(self, lattice: Lattice, mode_type: str) -> float:
        """Compute effective sound velocity for information propagation"""
        if mode_type == "acoustic":
            return lattice.compute_acoustic_velocity()
        else:
            return lattice.compute_optical_velocity()

    def _compute_group_velocity(self, v_s: float, k_vector: np.ndarray) -> float:
        """Compute group velocity v_g = dω/dk"""
        # For linear dispersion ω = v_s*k, group velocity equals phase velocity v_s.
        return v_s

    def _compute_bandwidth(self, frequency: float) -> float:
        """Placeholder to compute bandwidth from frequency."""
        return frequency * 1000

    def _compute_latency_improvement(self, communication_graph: CommunicationGraph, flow_optimizations: List[OptimizedChannel]) -> float:
        """Placeholder for computing latency improvement."""
        if not flow_optimizations:
            return 0.0
        old_velocity = 0.5 # Assumed old velocity
        new_avg_velocity = sum(opt.group_velocity for opt in flow_optimizations) / len(flow_optimizations)
        return (new_avg_velocity / old_velocity) - 1.0 if old_velocity > 0 else 0.0

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measure the total potential information throughput (bandwidth)."""
        # Mock measurement based on system state parameters
        mock_nodes = [Node(id=f'n{i}') for i in range(system_state.module_count)]
        mock_graph = CommunicationGraph(nodes=mock_nodes, edges=[])

        flow_optimization_result = self.apply_physics_principle(mock_graph)

        return Observable(
            name="total_potential_bandwidth",
            value=flow_optimization_result.total_bandwidth,
            unit="kbps"
        )
