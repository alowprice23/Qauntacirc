import datetime
import numpy as np
import math
import sys

from core.orchestrator import Orchestrator
from core.energy_calculator import EnergyCalculator
from core.two_phase_annealer import TwoPhaseAnnealer
from core.lyapunov_monitor import LyapunovMonitor
from core.closure_validator import ClosureValidator
from core.agent_pool import AgentPool
from core.types import (
    SystemState,
    Agent,
    Module,
    DependencyGraph,
    Constraint,
    Obligation,
    EnergyBreakdown,
    LyapunovMetrics,
    ObligationType,
    ObligationStatus,
    ProofWitness,
)

def setup_system() -> tuple[Orchestrator, list[Agent], SystemState]:
    """
    Initializes all components and creates a sample initial state.
    """
    energy_calculator = EnergyCalculator(alpha=1.0, beta=1.0, gamma=2.0, delta=0.5)
    lyapunov_monitor = LyapunovMonitor(kappa=100.0, xi=50.0)
    annealer = TwoPhaseAnnealer()
    closure_validator = ClosureValidator()
    agents = [Agent(id=f"agent_{i}", name=f"Agent-{i:02d}") for i in range(10)]
    agent_pool = AgentPool(agents=agents)

    orchestrator = Orchestrator(
        energy_calculator=energy_calculator,
        lyapunov_monitor=lyapunov_monitor,
        annealer=annealer,
        agent_pool=agent_pool,
        closure_validator=closure_validator,
    )

    # Construct a sample initial SystemState
    modules = [
        Module(name="auth", normalized_ast=b"", semantic_tokens=[], cyclomatic_complexity=5.0, duplication_factor=0.1, coverage_deficit=0.3, last_refactor=datetime.datetime.now()),
        Module(name="payment", normalized_ast=b"", semantic_tokens=[], cyclomatic_complexity=12.0, duplication_factor=0.2, coverage_deficit=0.5, last_refactor=datetime.datetime.now()),
        Module(name="profile", normalized_ast=b"", semantic_tokens=[], cyclomatic_complexity=2.0, duplication_factor=0.0, coverage_deficit=0.1, last_refactor=datetime.datetime.now()),
    ]

    # Use the annealer's internal demo energy calculation to set the initial state energy
    # This ensures consistency throughout the demonstration.
    initial_demo_energy = annealer._calculate_demo_energy(SystemState(modules=modules, energy_breakdown=EnergyBreakdown(total=0, complexity=0, coupling=0, constraint=0, debt=0), lyapunov_metrics=LyapunovMetrics(phi=0, energy=0, test_penalty=0, obligation_penalty=0)))

    initial_state = SystemState(
        modules=modules,
        dependency_graph=None,
        constraints=[],
        obligations=[Obligation(id="SEC-001",type=ObligationType.SECURITY,description="",status=ObligationStatus.OPEN,energy_impact=50.0)],
        failing_tests=["test_login_failure"],
        energy_breakdown=EnergyBreakdown(total=initial_demo_energy, complexity=initial_demo_energy, coupling=0, constraint=0, debt=0),
        lyapunov_metrics=LyapunovMetrics(phi=0, energy=0, test_penalty=0, obligation_penalty=0) # Will be calculated
    )

    return orchestrator, agents, initial_state

def main():
    """
    Runs the main simulation loop to demonstrate the orchestration system.
    """
    orchestrator, agents, current_state = setup_system()
    print("✅ System initialized successfully!")

    max_iterations = 200
    c_cooling_const = 10.0
    energy_history = []
    gradient_history = []

    print("\n" + "="*70)
    print("--- Starting Simulation ---")
    print("="*70)

    for k in range(max_iterations):
        evolution = orchestrator.evolve_system(current_state, agents, k, c_cooling_const)
        current_state = evolution.final_state

        energy_history.append(current_state.energy_breakdown.total)
        gradient_history.append(orchestrator.annealer._compute_energy_gradient(current_state))

        print(
            f"Iter {k:03d} | "
            f"Phase: {current_state.phase} | "
            f"Energy: {current_state.energy_breakdown.total:6.2f} | "
            f"Lyapunov Φ: {current_state.lyapunov_metrics.phi:6.2f} | "
            f"λ: {current_state.contraction_factor:.3f}"
        )

        if current_state.phase == "A":
            if orchestrator.annealer.detect_basin_capture(energy_history, gradient_history):
                print("\n" + "="*70)
                print(f"🚀 PHASE TRANSITION DETECTED AT ITERATION {k}! Switching to Phase B.")
                print("="*70 + "\n")
                current_state.phase = "B"

        elif current_state.phase == "B":
            if evolution.final_state.contraction_factor >= 1.0 and evolution.initial_state.contraction_factor < 1.0:
                print("\n--- Convergence Reached in Phase B ---")
                break
            gradient_norm = np.linalg.norm(orchestrator.annealer._compute_energy_gradient(current_state))
            if gradient_norm < orchestrator.annealer.convergence_tolerance:
                print("\n--- Convergence Reached in Phase B (Gradient Norm) ---")
                break

    print("\n" + "="*70)
    print("--- Simulation Finished ---")
    print("="*70)
    print(f"Final State Energy:     {current_state.energy_breakdown.total:.2f}")
    print(f"Final Lyapunov Potential: {current_state.lyapunov_metrics.phi:.2f}")


if __name__ == "__main__":
    main()
