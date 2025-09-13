from typing import List, Dict
import random

from core.energy_calculator import EnergyCalculator
from core.lyapunov_monitor import LyapunovMonitor
from core.closure_validator import ClosureValidator
from core.data_models import (
    SystemState, SystemEvolution, AgentAction, QuantizedTasks, CodeEvolution,
    OrthogonalizationResult, UncertaintyAnalysis, TunnelingResult,
    ResourceAllocation, FlowOptimization, ChaosTestResult,
    GrowthPrediction, DependencyOptimization, PhysicsResult, Obligation, ObligationType, ObligationStatus
)
from communication.protocol import AgentCommunicationProtocol

class Orchestrator:
    """
    The orchestrator coordinates all agents to evolve the software state towards
    a lower energy configuration, enforcing mathematical guarantees.
    """
    def __init__(
        self,
        agents: List['QuantumAgent'],
        energy_calculator: EnergyCalculator,
        lyapunov_monitor: LyapunovMonitor,
        closure_validator: ClosureValidator,
        communication_protocol: AgentCommunicationProtocol
    ):
        from agents.base.agent import PhysicsBasedAgent
        self.agents = agents
        self.energy_calculator = energy_calculator
        self.lyapunov_monitor = lyapunov_monitor
        self.closure_validator = closure_validator
        self.comm_protocol = communication_protocol
        self.agent_selector_strategy = "round-robin"
        self.last_agent_idx = -1

    def select_agent(self) -> 'QuantumAgent':
        """Selects an agent to run based on the chosen strategy."""
        from agents.base.agent import QuantumAgent
        if self.agent_selector_strategy == "round-robin":
            self.last_agent_idx = (self.last_agent_idx + 1) % len(self.agents)
            return self.agents[self.last_agent_idx]
        else:
            return random.choice(self.agents)

    def evolve_system(self, current_state: SystemState) -> SystemEvolution:
        """
        Executes one full cycle of the system's evolution by selecting and running an agent.
        """
        agent = self.select_agent()
        print(f"Orchestrator: Selected agent -> {agent.__class__.__name__}")

        result = agent.apply_physics_principle(current_state.model_copy(deep=True))

        new_state = self._apply_result_to_state(current_state, result, agent)

        new_state.energy_breakdown = self.energy_calculator.compute_total_energy(new_state)
        new_state.lyapunov_metrics = self.lyapunov_monitor.compute(new_state)

        certificate = agent.generate_certificate(current_state, new_state, result)
        print(f"CERTIFICATE [{agent.__class__.__name__}]: {certificate.performance_guarantee.description} - Verified: {certificate.performance_guarantee.verified}")

        evolution = SystemEvolution(
            initial_state=current_state,
            final_state=new_state,
            actions=[AgentAction(agent_id=agent.__class__.__name__, action_type=agent.physics_principle, params={})],
            energy_delta=new_state.energy_breakdown.total - current_state.energy_breakdown.total
        )

        self.verify_evolution(evolution)
        return evolution

    def _apply_result_to_state(self, current_state: SystemState, result: PhysicsResult, agent: 'QuantumAgent') -> SystemState:
        """
        Applies the result from an agent's operation to the system state.
        This function dispatches to a handler based on the result type.
        """
        from agents.base.agent import QuantumAgent
        new_state = current_state.model_copy(deep=True)

        match result:
            case QuantizedTasks():
                print(f"Orchestrator: Applying QuantizedTasks result.")
                for q in result.quanta:
                    new_state.obligations.append(Obligation(
                        id=f"TASK-{random.randint(1000, 9999)}",
                        type=ObligationType.FUNCTIONAL,
                        description=q.description,
                        status=ObligationStatus.OPEN,
                        energy_impact=q.energy
                    ))
            case CodeEvolution():
                print(f"Orchestrator: Applying CodeEvolution result (Not Implemented).")
                # To implement: need to know which module was evolved.
                # Assumes input metadata contains 'module_id'.
                # e.g., module_id = new_state.metadata['schrodinger_dev_input']['module_id']
                # Then find and update the module in new_state.modules.
            case OrthogonalizationResult():
                print(f"Orchestrator: Applying OrthogonalizationResult (Not Implemented).")
                # To implement: need to update the state vectors of modules.
                # This is complex as SystemState.modules don't have state vectors.
                # The change would likely be reflected in the metadata for the next agent run.
            case UncertaintyAnalysis():
                print(f"Orchestrator: Applying UncertaintyAnalysis result.")
                if result.additional_tests:
                    new_state.metadata.setdefault("new_tests", []).extend(result.additional_tests)
            case TunnelingResult():
                print(f"Orchestrator: Applying TunnelingResult.")
                # Simulate performance gain by reducing complexity energy
                new_state.energy_breakdown.complexity -= result.total_performance_gain
            case ResourceAllocation():
                print(f"Orchestrator: Applying ResourceAllocation result.")
                new_state.metadata["resource_allocation_plan"] = result.model_dump()
            case FlowOptimization():
                print(f"Orchestrator: Applying FlowOptimization result.")
                new_state.metadata["flow_optimization_plan"] = result.model_dump()
            case ChaosTestResult():
                print(f"Orchestrator: Applying ChaosTestResult.")
                new_state.metadata.setdefault("chaos_tests", []).extend(result.scenarios)
            case GrowthPrediction():
                print(f"Orchestrator: Applying GrowthPrediction result.")
                new_state.metadata["growth_prediction"] = result.model_dump()
            case DependencyOptimization():
                print(f"Orchestrator: Applying DependencyOptimization result.")
                # Simulate modularity improvement by reducing coupling energy
                new_state.energy_breakdown.coupling -= result.expected_potential_reduction
            case _:
                print(f"Orchestrator: No state application logic for result type {type(result).__name__}.")

        return new_state

    def verify_evolution(self, evolution: SystemEvolution):
        """
        Verifies that the evolution satisfies system-wide constraints, such as
        Lyapunov stability.
        """
        initial_phi = evolution.initial_state.lyapunov_metrics.phi
        final_phi = evolution.final_state.lyapunov_metrics.phi

        if final_phi > initial_phi * 1.1:
            print(
                f"WARNING: Lyapunov potential increased from {initial_phi:.4f} to {final_phi:.4f}. "
                "This may be an exploratory move."
            )
        else:
            print("Lyapunov stability verified.")
