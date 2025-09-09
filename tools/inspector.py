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

from collections import Counter
from typing import List, Any, Dict

# Assuming access to agent and core types
from agents.base.agent import QuantumAgent
from core.types import QuantumState, AgentResult, Status

class Inspector:
    """
    Provides methods to inspect various parts of the QuantaCirc system.
    """
    def __init__(self):
        pass

    def inspect_quantum_state(self, state: QuantumState, verbose=False):
        """
        Provides a detailed inspection of a quantum state object.

        Args:
            state (QuantumState): The quantum state object to inspect.
            verbose (bool): If True, prints more detailed information.
        """
        print("\n--- Quantum State Inspection ---")
        if not isinstance(state, QuantumState):
            print("  Error: Object is not a valid QuantumState.")
            return

        print(f"  Measurement Basis: {state.measurement_basis}")

        if state.state_vector:
            sv = np.array(state.state_vector)
            num_qubits = int(np.log2(len(sv)))
            print(f"  Number of Qubits: {num_qubits}")
            print(f"  State Vector Norm: {np.linalg.norm(sv):.6f}")

            if verbose:
                print("  State Vector (complex values):")
                for i, amp in enumerate(sv):
                    print(f"    |{i:0{num_qubits}b}>: {amp.real:.4f} + {amp.imag:.4f}j")

            print("  Probabilities:")
            probabilities = np.abs(sv)**2
            for i, prob in enumerate(probabilities):
                if prob > 1e-6: # Only show non-trivial probabilities
                    print(f"    P(|{i:0{num_qubits}b}>): {prob:.4f}")

        if state.density_matrix:
            dm = np.array(state.density_matrix)
            print(f"\n  Density Matrix Shape: {dm.shape}")
            print(f"  Density Matrix Trace: {np.trace(dm):.6f}")
            if verbose:
                print("  Density Matrix:")
                print(np.round(dm, 4))

        print("------------------------------\n")

    def inspect_agent_memory(self, agent: QuantumAgent, last_n: int = 5):
        """
        Inspects the recent memory of an agent.
        NOTE: This assumes agent has a `memory` attribute with a `history`.
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

    def analyze_agent_behavior(self, results: List[AgentResult]):
        """
        Analyzes a list of agent results to summarize behavior.
        """
        print("\n--- Agent Behavior Analysis ---")
        if not results:
            print("  No agent results to analyze.")
            return

        total_results = len(results)
        status_counts = Counter(res.status for res in results)
        agent_counts = Counter(res.agent_name for res in results)

        print(f"  Total Results: {total_results}")
        print(f"  Status Breakdown: {dict(status_counts)}")
        print(f"  Agent Activity: {dict(agent_counts)}")

        total_energy_delta = 0
        for res in results:
            if res.energy_delta and 'interaction' in res.energy_delta:
                total_energy_delta += res.energy_delta['interaction']

        print(f"  Total Interaction Energy Delta: {total_energy_delta:.4f}")
        print("---------------------------------\n")


    def introspect_object(self, obj: Any):
        """
        Performs a generic introspection on any object.
        """
        print(f"\n--- Object Introspection: {type(obj).__name__} ---")
        print(f"  ID: {id(obj)}")

        attributes = []
        for attr in dir(obj):
            if not attr.startswith('__'):
                try:
                    if not callable(getattr(obj, attr)):
                        attributes.append(attr)
                except AttributeError:
                    # Handle class-only attributes like Pydantic's __signature__
                    pass

        methods = [attr for attr in dir(obj) if not attr.startswith('__') and callable(getattr(obj, attr))]

        print(f"  Attributes ({len(attributes)}): {attributes}")
        print(f"  Methods ({len(methods)}): {methods}")
        print("--------------------------------------\n")


if __name__ == '__main__':
    # --- Example Usage ---
    from uuid import uuid4

    # Use real types now
    from core.types import QuantumState, AgentResult, Status

    # Mock agent for memory inspection
    class MockMemory:
        def __init__(self):
            self.history = ["Event 1", "Event 2", "Decision A"]

    class MockAgent(QuantumAgent):
        def __init__(self, name):
            self.name = name
            self.memory = MockMemory()
        async def analyze_state(self, state): pass
        def validate_proposal(self, proposal): pass
        def execute(self, proposal): pass


    inspector = Inspector()

    # 1. Inspect a quantum state
    bell_state = QuantumState(
        state_vector=[complex(1/np.sqrt(2)), 0, 0, complex(1/np.sqrt(2))],
        density_matrix=[[0.5, 0, 0, 0.5], [0, 0, 0, 0], [0, 0, 0, 0], [0.5, 0, 0, 0.5]]
    )
    inspector.inspect_quantum_state(bell_state, verbose=True)

    # 2. Inspect an agent's memory
    my_agent = MockAgent("PauliGuard")
    inspector.inspect_agent_memory(my_agent)

    # 3. Analyze agent behavior
    agent_results = [
        AgentResult(task_id=uuid4(), agent_name="PauliGuard", action_taken=True, status=Status.SUCCESS, energy_delta={"interaction": -10.5}),
        AgentResult(task_id=uuid4(), agent_name="SchrodingerDev", action_taken=True, status=Status.SUCCESS, energy_delta={"interaction": 5.2}),
        AgentResult(task_id=uuid4(), agent_name="PauliGuard", action_taken=False, status=Status.FAILED, error="Duplicate not found"),
    ]
    inspector.analyze_agent_behavior(agent_results)

    # 4. Introspect a generic object
    inspector.introspect_object(bell_state)
