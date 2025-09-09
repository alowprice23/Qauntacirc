# tools/inspector.py
"""
Advanced debugging and inspection tools for QuantaCirc.

This module provides utilities for runtime inspection of quantum states, agent
behavior, and other internal states of the system. It is invaluable for
advanced debugging and analysis.

Key Features:
- Inspection of quantum state objects.
- Analysis of agent memory and decision-making processes.
- Tools for runtime object introspection.
"""

import numpy as np
from typing import Any, Dict

# Assuming access to agent and core types
# from agents.base.agent import BaseAgent
# from core.types import QuantumState

class Inspector:
    """
    Provides methods to inspect various parts of the QuantaCirc system.
    """
    def __init__(self):
        pass

    def inspect_quantum_state(self, state: Any, verbose=False):
        """
        Provides a detailed inspection of a quantum state object.

        Args:
            state (QuantumState): The quantum state object to inspect.
            verbose (bool): If True, prints more detailed information.
        """
        print("\n--- Quantum State Inspection ---")
        if not hasattr(state, 'vector') or not isinstance(state.vector, np.ndarray):
            print("  Error: Object does not appear to be a valid quantum state.")
            return

        print(f"  State Type: {type(state).__name__}")
        print(f"  Number of Qubits: {int(np.log2(len(state.vector)))}")
        print(f"  Norm: {np.linalg.norm(state.vector):.6f}")

        if verbose:
            print("  State Vector (complex values):")
            for i, amp in enumerate(state.vector):
                print(f"    |{i:02b}>: {amp:.4f}")

        print("  Probabilities:")
        probabilities = np.abs(state.vector)**2
        for i, prob in enumerate(probabilities):
            print(f"    P(|{i:02b}>): {prob:.4f}")
        print("------------------------------\n")

    def inspect_agent_memory(self, agent: Any, last_n: int = 5):
        """
        Inspects the recent memory of an agent.

        Args:
            agent (BaseAgent): The agent instance to inspect.
            last_n (int): The number of recent memory entries to show.
        """
        print(f"\n--- Agent Memory Inspection: {agent.name} ---")
        if not hasattr(agent, 'memory') or not hasattr(agent.memory, 'history'):
            print("  Error: Agent does not have a recognizable memory structure.")
            return

        recent_history = agent.memory.history[-last_n:]
        if not recent_history:
            print("  Memory is empty.")
        else:
            print(f"  Showing last {len(recent_history)} of {len(agent.memory.history)} entries:")
            for i, entry in enumerate(recent_history):
                print(f"    - Entry {-len(recent_history)+i}: {entry}")
        print("------------------------------------------\n")

    def introspect_object(self, obj: Any):
        """
        Performs a generic introspection on any object.
        """
        print(f"\n--- Object Introspection: {type(obj).__name__} ---")
        print(f"  ID: {id(obj)}")
        attributes = [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith('__')]
        methods = [attr for attr in dir(obj) if callable(getattr(obj, attr)) and not attr.startswith('__')]

        print(f"  Attributes ({len(attributes)}): {attributes}")
        print(f"  Methods ({len(methods)}): {methods}")
        print("--------------------------------------\n")


if __name__ == '__main__':
    # --- Example Usage ---

    # Create mock objects for demonstration, as we don't have the actual classes here
    class MockQuantumState:
        def __init__(self, vector):
            self.vector = vector

    class MockMemory:
        def __init__(self):
            self.history = ["Event 1", "Event 2", "Decision A"]

    class MockAgent:
        def __init__(self, name):
            self.name = name
            self.memory = MockMemory()

    inspector = Inspector()

    # 1. Inspect a quantum state
    # State is 1/sqrt(2) * (|00> + |11>)
    bell_state_vector = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)])
    state_obj = MockQuantumState(bell_state_vector)
    inspector.inspect_quantum_state(state_obj, verbose=True)

    # 2. Inspect an agent's memory
    my_agent = MockAgent("PauliGuard")
    inspector.inspect_agent_memory(my_agent)

    # 3. Introspect a generic object
    inspector.introspect_object(my_agent)
