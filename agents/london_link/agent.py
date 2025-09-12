import numpy as np
from typing import List, Dict, Any

from common.base_agent import PhysicsBasedAgent
from common.data_models import (
    DependencyGraph, Dependency, DependencyOptimization, DependencyOptimizationMove,
    Component, SystemState, Observable
)
from common.utils import DependencyOptimizer, LondonCoefficientCalculator

class LondonLinkAgent(PhysicsBasedAgent):
    def __init__(self):
        super().__init__(
            physics_principle="van der Waals Forces",
            mathematical_formula="V(r) = -C₆/r⁶"
        )
        self.dependency_optimizer = DependencyOptimizer()
        self.C6_calculator = LondonCoefficientCalculator()

    def apply_physics_principle(self, dependency_graph: DependencyGraph, **kwargs) -> DependencyOptimization:
        """Optimize long-range dependencies using van der Waals model"""
        num_nodes = len(dependency_graph.nodes)
        if num_nodes < 2:
            return DependencyOptimization(original_potential=0, optimized_moves=[], expected_potential_reduction=0, modularity_improvement=0)

        london_coefficients = self._compute_all_london_coefficients(dependency_graph.nodes)

        potential_matrix = np.zeros((num_nodes, num_nodes))
        node_map = {node.id: i for i, node in enumerate(dependency_graph.nodes)}

        for i, node_i in enumerate(dependency_graph.nodes):
            for j, node_j in enumerate(dependency_graph.nodes):
                if i >= j: continue

                r_ij = self._compute_component_distance(node_i, node_j, dependency_graph)

                if r_ij > 1e-9:
                    C6_ij = london_coefficients.get((node_i.id, node_j.id), 1.0)
                    potential = -C6_ij / (r_ij ** 6)
                    potential_matrix[i][j] = potential
                    potential_matrix[j][i] = potential

        optimization_moves = self.dependency_optimizer.find_optimal_structure(
            current_graph=dependency_graph,
            potential_matrix=potential_matrix,
            constraints=self._extract_dependency_constraints(dependency_graph)
        )

        return DependencyOptimization(
            original_potential=np.sum(potential_matrix) / 2, # Divide by 2 as matrix is symmetric
            optimized_moves=optimization_moves,
            expected_potential_reduction=self._compute_potential_reduction(optimization_moves),
            modularity_improvement=self._compute_modularity_improvement(optimization_moves)
        )

    def _compute_all_london_coefficients(self, nodes: List[Component]) -> Dict[tuple[str, str], float]:
        """Pre-compute all C6 coefficients for all pairs."""
        coeffs = {}
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if i >= j: continue
                C6_ij = self.C6_calculator.compute_coefficient(node_i, node_j)
                coeffs[(node_i.id, node_j.id)] = C6_ij
                coeffs[(node_j.id, node_i.id)] = C6_ij
        return coeffs

    def _compute_component_distance(self, comp_i: Component, comp_j: Component, graph: DependencyGraph) -> float:
        """Compute effective distance between components based on coupling strength."""
        coupling = self._measure_coupling_strength(comp_i, comp_j, graph)
        return 1.0 / (coupling + 1e-6)

    def _measure_coupling_strength(self, comp_i: Component, comp_j: Component, graph: DependencyGraph) -> float:
        """Placeholder to measure coupling strength between two components."""
        # Check for a direct edge in the provided graph
        for edge in graph.edges:
            if (edge.source.id == comp_i.id and edge.target.id == comp_j.id) or \
               (edge.source.id == comp_j.id and edge.target.id == comp_i.id):
                return edge.strength
        # If no direct edge, coupling is considered weak (but non-zero for potential calculation)
        return 0.01

    def _extract_dependency_constraints(self, dependency_graph: DependencyGraph) -> List[Any]:
        """Placeholder to extract dependency constraints."""
        return []

    def _compute_potential_reduction(self, optimization_moves: List[DependencyOptimizationMove]) -> float:
        """Computes the total expected potential reduction from moves."""
        return sum(move.potential_reduction for move in optimization_moves)

    def _compute_modularity_improvement(self, optimization_moves: List[DependencyOptimizationMove]) -> float:
        """Placeholder to compute modularity improvement."""
        return 0.05 * len(optimization_moves)

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measure the total dependency potential energy of the system."""
        if system_state.module_count < 2:
            return Observable(name="dependency_potential", value=0.0, unit="energy")

        components = [Component(id=f'comp_{i}', properties={'polarizability': np.random.uniform(0.5, 1.5)}) for i in range(system_state.module_count)]
        mock_graph = DependencyGraph(nodes=components, edges=[]) # Assume a graph with no explicit edges for this measurement

        result = self.apply_physics_principle(mock_graph)

        return Observable(
            name="dependency_potential",
            value=result.original_potential,
            unit="energy"
        )
