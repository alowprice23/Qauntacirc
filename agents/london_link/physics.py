import numpy as np
from typing import List, Dict, Any
from core.types import DependencyGraph, Component
from common.utils import LondonCoefficientCalculator

class VanDerWaals:
    def __init__(self):
        self.C6_calculator = LondonCoefficientCalculator()

    def compute_london_coefficients(self, graph: DependencyGraph) -> Dict[tuple[str, str], float]:
        """Computes the London C₆ coefficients for all component pairs."""
        coefficients = {}
        for i in range(len(graph.nodes)):
            for j in range(i + 1, len(graph.nodes)):
                comp_i, comp_j = graph.nodes[i], graph.nodes[j]
                c6_ij = self.C6_calculator.compute_coefficient(comp_i, comp_j)
                coefficients[(comp_i.id, comp_j.id)] = c6_ij
        return coefficients

    def compute_potential_matrix(self, graph: DependencyGraph, coefficients: Dict[tuple[str, str], float]) -> np.ndarray:
        """Computes the potential energy V(r) = -C₆/r⁶ for all pairs."""
        num_nodes = len(graph.nodes)
        potential_matrix = np.zeros((num_nodes, num_nodes))

        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                node_i, node_j = graph.nodes[i], graph.nodes[j]
                r_ij = self.compute_component_distance(node_i, node_j, graph)
                if r_ij > 0:
                    key = (node_i.id, node_j.id) if (node_i.id, node_j.id) in coefficients else (node_j.id, node_i.id)
                    C6_ij = coefficients.get(key, 1.0)
                    potential = -C6_ij / (r_ij ** 6)
                    potential_matrix[i, j] = potential_matrix[j, i] = potential
        return potential_matrix

    def compute_component_distance(self, comp_i: Component, comp_j: Component, graph: DependencyGraph) -> float:
        """Distance is inversely related to coupling strength."""
        coupling = self.measure_coupling_strength(comp_i, comp_j, graph)
        return 1.0 / (coupling + 1e-6)

    def measure_coupling_strength(self, comp_i: Component, comp_j: Component, graph: DependencyGraph) -> float:
        """Measures coupling based on component 'polarizability' and direct dependencies."""
        polar_i = comp_i.properties.get("polarizability", 0.1)
        polar_j = comp_j.properties.get("polarizability", 0.1)
        base_coupling = polar_i * polar_j

        direct_strength = 0.0
        for edge in graph.edges:
            if (edge.source.id, edge.target.id) in [(comp_i.id, comp_j.id), (comp_j.id, comp_i.id)]:
                direct_strength = edge.strength
                break
        return base_coupling + direct_strength
