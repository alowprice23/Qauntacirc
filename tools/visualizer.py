# tools/visualizer.py
"""
Visualization tools for QuantaCirc.

This module provides utilities for creating visual representations of quantum
states, energy landscapes, and agent interactions. Visualizations are critical
for debugging, analysis, and understanding the behavior of the system.

Key Features:
- Plotting of quantum state vectors and density matrices.
- 3D visualization of energy landscapes.
- Generation of diagrams for agent communication and workflow.

NOTE: This module depends on external plotting libraries like Matplotlib or Plotly.
The code provides a structural outline; actual plotting commands are commented out
to avoid hard dependencies in a core tool.
"""

import numpy as np
from typing import List, Tuple, Dict

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import graphviz
from typing import Optional

class Visualizer:
    """
    Handles the creation of various plots and diagrams.
    """
    def __init__(self, backend='matplotlib'):
        self.backend = backend
        print(f"Visualizer initialized with backend: {self.backend}")

    def plot_quantum_state(self, state_vector: np.ndarray, title: str = "Quantum State", output_path: Optional[str] = None):
        """
        Visualizes a quantum state vector using a bar chart for probabilities.

        Args:
            state_vector (np.ndarray): A 1D numpy array representing the state vector.
            title (str): The title of the plot.
            output_path (str, optional): If provided, saves the plot to this file path.
        """
        if not isinstance(state_vector, np.ndarray) or state_vector.ndim != 1:
            raise ValueError("state_vector must be a 1D numpy array.")

        probabilities = np.abs(state_vector)**2
        num_states = len(probabilities)
        state_labels = [f"|{i}>" for i in range(num_states)]

        plt.figure()
        plt.bar(state_labels, probabilities)
        plt.title(title)
        plt.ylabel("Probability")
        plt.xlabel("Basis State")

        if output_path:
            plt.savefig(output_path)
            print(f"Quantum state plot saved to {output_path}")
        else:
            plt.show()
        plt.close()


    def plot_energy_landscape(self, X, Y, Z, title="Energy Landscape", output_path: Optional[str] = None):
        """
        Creates a 3D surface plot of an energy landscape.

        Args:
            X, Y, Z (np.ndarray): 2D arrays representing the coordinates and energy values.
            title (str): The title of the plot.
            output_path (str, optional): If provided, saves the plot to this file path.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis')
        ax.set_title(title)
        ax.set_xlabel("Parameter 1")
        ax.set_ylabel("Parameter 2")
        ax.set_zlabel("Energy")

        if output_path:
            plt.savefig(output_path)
            print(f"Energy landscape plot saved to {output_path}")
        else:
            plt.show()
        plt.close()


    def draw_agent_interaction_graph(self, interactions: List[Tuple[str, str, str]], output_path: str = "agent_interactions"):
        """
        Generates a diagram of agent interactions using Graphviz.

        Args:
            interactions (List[Tuple[str, str, str]]): A list of tuples, where each
                tuple is (source_agent, dest_agent, message_type).
            output_path (str): The base path for the output file (e.g., 'graph'). Extension will be '.png'.
        """
        dot = graphviz.Digraph(comment='Agent Interaction Diagram')
        for source, dest, msg in interactions:
            dot.edge(source, dest, label=msg)

        try:
            # Render the graph to a file
            output_filename = f"{output_path}.gv"
            dot.render(output_filename, format='png', view=False, cleanup=True)
            print(f"Agent interaction diagram saved to {output_filename}.png")
        except Exception as e:
            print(f"Could not render graph. Is Graphviz installed and in your PATH? Error: {e}")


if __name__ == '__main__':
    # Example Usage
    # Note: plt.show() is disabled in this non-interactive example.
    # We will save plots to files instead.
    vis = Visualizer()

    # 1. Quantum State Visualization
    plus_state = np.array([1/np.sqrt(2), 1/np.sqrt(2)])
    vis.plot_quantum_state(plus_state, "Bell State |+>", output_path="quantum_state.png")

    # 2. Energy Landscape
    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(np.sqrt(X**2 + Y**2)) # Example energy function
    vis.plot_energy_landscape(X, Y, Z, output_path="energy_landscape.png")

    # 3. Agent Interactions
    agent_flow = [
        ("Orchestrator", "PauliGuard", "AnalyzeRequest"),
        ("PauliGuard", "EnergyCalculator", "GetEnergy"),
        ("EnergyCalculator", "PauliGuard", "ReturnEnergy"),
        ("PauliGuard", "Orchestrator", "AnalysisComplete"),
    ]
    vis.draw_agent_interaction_graph(agent_flow, output_path="agent_interactions")
