import datetime
import numpy as np
import math
import sys
import asyncio

from core.orchestrator import Orchestrator
from core.energy_calculator import EnergyCalculator
from core.lyapunov_monitor import LyapunovMonitor
from core.closure_validator import ClosureValidator
from communication.protocol import AgentCommunicationProtocol
from core.data_models import (
    SystemState, Module, DependencyGraph, Constraint, Obligation,
    EnergyBreakdown, LyapunovMetrics, ObligationType, ObligationStatus, SoftwareState
)

# Import all the agents
from agents.planck_forge.agent import PlanckForgeAgent
from agents.schrodinger_dev.agent import SchrödingerDevAgent
from agents.pauli_guard.agent import PauliGuardAgent
from agents.uncertain_ai.agent import UncertainAIAgent
from agents.tunnel_fix.agent import TunnelFixAgent
from agents.bose_boost.agent import BoseBoostAgent
from agents.phonon_flow.agent import PhononFlowAgent
from agents.fluctua_test.agent import FluctuaTestAgent
from agents.hydro_spread.agent import HydroSpreadAgent
from agents.london_link.agent import LondonLinkAgent

def setup_system() -> tuple[Orchestrator, SystemState]:
    """
    Initializes all components and creates a sample initial state.
    """
    energy_calculator = EnergyCalculator(alpha=1.0, beta=1.0, gamma=2.0, delta=0.5)
    lyapunov_monitor = LyapunovMonitor(kappa=100.0, xi=50.0)
    closure_validator = ClosureValidator()
    comm_protocol = AgentCommunicationProtocol()

    # Instantiate all the real agents
    agents = [
        PlanckForgeAgent(),
        SchrödingerDevAgent(),
        PauliGuardAgent(),
        UncertainAIAgent(),
        TunnelFixAgent(),
        BoseBoostAgent(),
        PhononFlowAgent(),
        FluctuaTestAgent(),
        HydroSpreadAgent(),
        LondonLinkAgent(),
    ]

    orchestrator = Orchestrator(
        agents=agents,
        energy_calculator=energy_calculator,
        lyapunov_monitor=lyapunov_monitor,
        closure_validator=closure_validator,
        communication_protocol=comm_protocol,
    )

    modules = [
        Module(name="auth", normalized_ast=b"auth_code", semantic_tokens=["def", "login"], cyclomatic_complexity=5.0, duplication_factor=0.1, coverage_deficit=0.3, last_refactor=datetime.datetime.now()),
        Module(name="payment", normalized_ast=b"payment_code", semantic_tokens=["class", "Payment"], cyclomatic_complexity=12.0, duplication_factor=0.2, coverage_deficit=0.5, last_refactor=datetime.datetime.now()),
    ]

    # Create a temporary state to calculate initial energy
    temp_state = SystemState(
        modules=modules,
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=0, complexity=0, coupling=0, constraint=0, debt=0),
        lyapunov_metrics=LyapunovMetrics(phi=0, energy=0, test_penalty=0, obligation_penalty=0)
    )
    initial_energy = energy_calculator.compute_total_energy(temp_state)

    # Add metadata for agents that require it
    metadata = {
        "schrodinger_dev_input": {
            "code_state": {
                "state_vector": [1, 0, 0, 0],
                "code": "def hello():\n    print('hello')"
            },
            "hamiltonian": {
                "matrix": [[1, 0.5, 0, 0], [0.5, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
            },
            "dt": 0.1
        },
        "pauli_guard_input": {
            "modules": [
                {"id": "auth", "state_vector": [1, 0.1, 0, 0], "code": "..." },
                {"id": "payment", "state_vector": [0.9, 0.2, 0, 0], "code": "..." }
            ]
        },
        "tunnel_fix_input": {
            "performance_profile": {"metrics": {"latency": 100.0, "error_rate": 0.05}}
        },
        "bose_boost_input": {
            "workload": {
                "tasks": {
                    "auth": {"complexity": 5.0},
                    "payment": {"complexity": 12.0}
                },
                "total_resources": 100.0,
                "max_replicas_per_task": 10
            },
            "temperature": 1.0
        },
        "hydro_spread_input": {
            "growth_parameters": {
                "density": 1.0,
                "gravity": 9.8,
                "time_horizons": [1, 12, 24]
            }
        },
        "fluctua_test_input": {
            "temperature": 1.0
        }
    }

    initial_state = SystemState(
        modules=modules,
        software_state=SoftwareState(),
        requirements=["The system must be secure.", "The system must be fast."],
        energy_breakdown=initial_energy,
        lyapunov_metrics=LyapunovMetrics(phi=0, energy=initial_energy.total, test_penalty=0, obligation_penalty=0),
        metadata=metadata
    )
    return orchestrator, initial_state

async def main():
    """
    Runs the main agent-driven loop.
    """
    orchestrator, current_state = setup_system()
    print("✅ System initialized successfully with 10 agents.")

    # Connect to NATS
    try:
        await orchestrator.comm_protocol.connect()
    except Exception as e:
        print(f"WARNING: Could not connect to NATS server. Continuing without communication features. Error: {e}")

    max_iterations = 20  # Run a few iterations to see different agents work

    print("\n" + "="*70)
    print("--- Starting Agent-Driven Evolution ---")
    print("="*70)

    for k in range(max_iterations):
        print(f"\n--- Iteration {k:03d} ---")
        evolution = orchestrator.evolve_system(current_state)
        current_state = evolution.final_state

        print(
            f"State | "
            f"Energy: {current_state.energy_breakdown.total:6.2f} | "
            f"Lyapunov Φ: {current_state.lyapunov_metrics.phi:6.2f}"
        )

    if orchestrator.comm_protocol.is_connected:
        await orchestrator.comm_protocol.close()

    print("\n" + "="*70)
    print("--- Simulation Finished ---")
    print("="*70)
    print(f"Final State Energy:     {current_state.energy_breakdown.total:.2f}")
    print(f"Final Lyapunov Potential: {current_state.lyapunov_metrics.phi:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
