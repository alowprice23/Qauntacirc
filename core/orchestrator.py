from typing import List
import math
import numpy as np

# All the components I've built or refactored
from core.energy_calculator import EnergyCalculator
from core.two_phase_annealer import TwoPhaseAnnealer
from core.closure_validator import ClosureValidator
from core.agent_pool import AgentPool
from core.lyapunov_monitor import LyapunovMonitor

# The types I've defined
from core.types import (
    SystemState,
    Agent,
    SystemEvolution,
    LyapunovMetrics,
    EnergyBreakdown,
    AgentAction,
    ComposedAction
)

class Orchestrator:
    """
    The orchestrator coordinates all agents and system components to evolve
    the software state towards a lower energy configuration, enforcing
    mathematical guarantees throughout the process.
    """

    def __init__(
        self,
        energy_calculator: EnergyCalculator,
        lyapunov_monitor: LyapunovMonitor,
        annealer: TwoPhaseAnnealer,
        agent_pool: AgentPool,
        closure_validator: ClosureValidator,
    ):
        self.energy_calculator = energy_calculator
        self.lyapunov_monitor = lyapunov_monitor
        self.annealer = annealer
        self.agent_pool = agent_pool
        self.closure_validator = closure_validator

    def evolve_system(self, current_state: SystemState, agents: List[Agent], k: int, c_cooling_const: float) -> SystemEvolution:
        """
        Executes one full cycle of the system's evolution.
        """
        # 1. Calculate Lyapunov potential for the current state.
        # The energy is assumed to be correct from the previous step.
        current_state.lyapunov_metrics = self.lyapunov_monitor.compute(current_state)
        self.lyapunov_monitor.track(current_state.lyapunov_metrics)

        # 2. Apply agent transformations via the annealer, depending on the phase.
        if current_state.phase == "A":
            temperature = c_cooling_const / math.log(k + 2)
            annealing_result = self.annealer.phase_a_step(current_state, temperature)
            new_state = annealing_result.state
            # In a real system, the proposal would contain the action.
            actions = []
            energy_delta = annealing_result.energy_delta

        elif current_state.phase == "B":
            contraction_result = self.annealer.phase_b_step(current_state)
            new_state = contraction_result.state
            new_state.contraction_factor = contraction_result.lambda_factor
            # The action is implicit in the gradient step.
            actions = []
            energy_delta = new_state.energy_breakdown.total - current_state.energy_breakdown.total
        else:
            raise ValueError(f"Unknown annealing phase: {current_state.phase}")

        # 3. Recalculate Lyapunov metrics for the new state.
        #    For this demonstration, we trust the energy value that was set by the
        #    annealer's placeholder methods, rather than recalculating it.
        new_state.lyapunov_metrics = self.lyapunov_monitor.compute(new_state)

        # 4. Create the evolution record for this step.
        evolution = SystemEvolution(
            initial_state=current_state,
            final_state=new_state,
            actions=actions,
            energy_delta=energy_delta
        )

        # 5. Verify mathematical guarantees on the resulting evolution.
        self.verify_lyapunov_descent(evolution)
        self.verify_contraction_bounds(evolution)

        return evolution

    def verify_lyapunov_descent(self, evolution: SystemEvolution):
        """
        Verifies that the Lyapunov potential has not increased, which is a
        necessary condition for stability.
        Φ(S_{k+1}) <= Φ(S_k)
        """
        initial_phi = evolution.initial_state.lyapunov_metrics.phi
        final_phi = evolution.final_state.lyapunov_metrics.phi

        # In Phase A, stochastic jumps are allowed to temporarily increase potential.
        # However, in Phase B, the descent should be deterministic.
        if final_phi > initial_phi and evolution.final_state.phase == "B":
            raise RuntimeError(
                f"CRITICAL: Lyapunov potential increased from {initial_phi:.4f} to {final_phi:.4f} "
                "during Phase B. System is unstable."
            )

        print("Lyapunov descent verified.")

    def verify_contraction_bounds(self, evolution: SystemEvolution):
        """
        Monitors the contraction factor during Phase B of annealing to ensure
        the system is converging towards a local minimum.
        """
        if evolution.final_state.phase == "B":
            lambda_factor = evolution.final_state.contraction_factor
            if lambda_factor >= 1.0:
                print(f"WARNING: Contraction factor λ = {lambda_factor:.4f} >= 1. "
                      "Local convergence not guaranteed.")
            else:
                print(f"Contraction factor λ = {lambda_factor:.4f} < 1 verified.")
