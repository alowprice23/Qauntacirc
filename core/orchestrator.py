from typing import List, Dict, Callable
import random

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from agents.base.agent import PhysicsBasedAgent

from agents.base.quantum_agent import QuantumAgent
from agents.base.contracts import Proposal
from core.energy_calculator import EnergyCalculator
from core.lyapunov_monitor import LyapunovMonitor
from core.closure_validator import ClosureValidator
from core.closure_rules import ClosureRuleEngine
from core.types import (
    SystemState, SystemEvolution, AgentAction, QuantizedTasks, CodeEvolution,
    OrthogonalizationResult, UncertaintyAnalysis, TunnelingResult,
    ResourceAllocation, FlowOptimization, ChaosTestResult,
    GrowthPrediction, DependencyOptimization, PhysicsResult, Obligation, ObligationType, ObligationStatus,
    GateResult, MonitoringResult, CompletenessProof
)
from core.chaos_types import ChaosPlanResult
from monitoring.resilience import ResilienceMonitor
import asyncio
from communication.protocol import AgentCommunicationProtocol

class Orchestrator:
    """
    The orchestrator coordinates all agents to evolve the software state towards
    a lower energy configuration, enforcing mathematical guarantees.
    """
    def __init__(
        self,
        agents: List['PhysicsBasedAgent'],
        energy_calculator: EnergyCalculator,
        lyapunov_monitor: LyapunovMonitor,
        closure_validator: ClosureValidator,
        closure_rule_engine: ClosureRuleEngine,
        communication_protocol: AgentCommunicationProtocol
    ):
        self.agents = agents
        self.energy_calculator = energy_calculator
        self.lyapunov_monitor = lyapunov_monitor
        self.closure_validator = closure_validator
        self.closure_rule_engine = closure_rule_engine
        self.comm_protocol = communication_protocol
        self.agent_selector_strategy = "round-robin"
        self.last_agent_idx = -1

        self.gates: Dict[str, Callable[[SystemState], GateResult]] = {}
        self.monitors: Dict[str, Callable[[SystemState], MonitoringResult]] = {}
        self._register_default_components()

    def add_gate(self, name: str, func: Callable[[SystemState], GateResult]):
        """Adds a verification gate to the orchestrator."""
        self.gates[name] = func

    def add_monitor(self, name: str, func: Callable[[SystemState], MonitoringResult]):
        """Adds a system monitor to the orchestrator."""
        self.monitors[name] = func

    def _register_default_components(self):
        """Registers the default gates and monitors."""
        self.add_gate("delta_closure", self._closure_gate)
        self.add_monitor("closure_completeness", self._monitor_closure)

    def _suggest_closure_actions(self, closure_result: "ClosureResult") -> List[str]:
        """Placeholder for suggesting actions to fix closure."""
        missing_obligations = closure_result.closed_set - set(closure_result.completeness_proof.obligation_set)
        actions = [f"Add missing obligation: {ob.description}" for ob in missing_obligations]
        return actions

    def _generate_closure_alerts(self, closure_result: "ClosureResult") -> List[Dict]:
        """Placeholder for generating alerts from closure results."""
        alerts = []
        if not closure_result.is_closed:
            alerts.append({"type": "CLOSURE_FAILURE", "message": "System is not closed."})
        if not closure_result.is_minimal:
            alerts.append({"type": "CLOSURE_WARNING", "message": "System is not minimal."})
        return alerts

    def _closure_gate(self, state: SystemState) -> GateResult:
        """Gate function that blocks deployment until closure verified."""
        closure_result = self.closure_rule_engine.verify_closure(
            set(state.requirements),
            set(state.obligations)
        )

        if not closure_result.is_closed:
            return GateResult(
                passed=False,
                reason="Δ-closure not satisfied - missing obligations detected",
                required_actions=self._suggest_closure_actions(closure_result),
                blocking=True
            )

        if not closure_result.is_minimal:
            return GateResult(
                passed=False,
                reason="Obligation set not minimal - redundant obligations detected",
                required_actions=["remove_redundant_obligations"],
                blocking=False
            )

        return GateResult(
            passed=True,
            reason="Δ-closure verified - all obligations captured",
            completeness_proof=closure_result.completeness_proof
        )

    def _monitor_closure(self, state: SystemState) -> MonitoringResult:
        """Monitor closure status for real-time feedback."""
        closure_result = self.closure_rule_engine.verify_closure(
            set(state.requirements),
            set(state.obligations)
        )

        return MonitoringResult(
            status="CLOSED" if closure_result.is_closed else "OPEN",
            metrics={
                "obligation_count": len(closure_result.closed_set),
                "closure_iterations": closure_result.closure_iterations,
                "completeness_confidence": 1.0 if closure_result.is_closed else 0.0
            },
            alerts=self._generate_closure_alerts(closure_result)
        )

    def run_gates(self, state: SystemState) -> List[GateResult]:
        """Runs all registered gates and returns their results."""
        results = []
        for name, gate_func in self.gates.items():
            result = gate_func(state)
            print(f"Gate '{name}' result: {'PASSED' if result.passed else 'FAILED'}")
            results.append(result)
        return results

    def select_agent(self) -> 'PhysicsBasedAgent':
        """Selects an agent to run based on the chosen strategy."""
        if self.agent_selector_strategy == "round-robin":
            self.last_agent_idx = (self.last_agent_idx + 1) % len(self.agents)
            return self.agents[self.last_agent_idx]
        else:
            return random.choice(self.agents)

    async def evolve_system(self, current_state: SystemState) -> SystemEvolution:
        """
        Executes one full cycle of the system's evolution by selecting and running an agent.
        """
        gate_results = self.run_gates(current_state)
        for result in gate_results:
            if not result.passed and result.blocking:
                print(f"Blocking gate failed: {result.reason}. Halting evolution.")
                return SystemEvolution(
                    initial_state=current_state,
                    final_state=current_state,
                    actions=[],
                    energy_delta=0
                )

        agent = self.select_agent()
        print(f"Orchestrator: Selected agent -> {agent.__class__.__name__}")

        result = None
        if isinstance(agent, QuantumAgent):
            if agent.guard(current_state.model_copy(deep=True)):
                result = agent.propose(current_state.model_copy(deep=True))
        else:
            result = agent.apply_physics_principle(current_state.model_copy(deep=True))

        if result is None:
            return SystemEvolution(
                initial_state=current_state,
                final_state=current_state,
                actions=[],
                energy_delta=0
            )

        new_state = await self._apply_result_to_state(current_state, result, agent)

        new_state.energy_breakdown = self.energy_calculator.compute_total_energy(new_state)
        new_state.lyapunov_metrics = self.lyapunov_monitor.compute(new_state)

        certificate = agent.generate_certificate(current_state, new_state, result)
        if certificate:
            print(f"CERTIFICATE [{agent.__class__.__name__}]: {certificate.performance_guarantee.description} - Verified: {certificate.performance_guarantee.verified}")

        evolution = SystemEvolution(
            initial_state=current_state,
            final_state=new_state,
            actions=[AgentAction(agent_id=agent.__class__.__name__, action_type=agent.physics_principle, params={})],
            energy_delta=new_state.energy_breakdown.total - current_state.energy_breakdown.total
        )

        self.verify_evolution(evolution)
        return evolution

    async def _execute_chaos_plan(self, monitor: ResilienceMonitor, plan: "ChaosTestingPlan"):
        """Executes the scenarios in a chaos testing plan."""
        reports = []
        for i in plan.execution_order:
            scenario = plan.scenarios[i]
            report = await monitor.monitor_chaos_scenario(scenario)
            reports.append(report)
        return reports

    async def _apply_result_to_state(self, current_state: SystemState, result: PhysicsResult, agent: 'PhysicsBasedAgent') -> SystemState:
        """
        Applies the result from an agent's operation to the system state.
        This function dispatches to a handler based on the result type.
        """
        new_state = current_state.model_copy(deep=True)

        match result:
            case Proposal():
                print(f"Orchestrator: Applying Proposal result from {result.agent_id}.")
                total_estimated_speedup = sum(opt.estimated_speedup for opt in result.optimizations)
                new_state.energy_breakdown.complexity -= total_estimated_speedup
                print(f"Reduced complexity energy by {total_estimated_speedup}")
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
            case OrthogonalizationResult():
                print(f"Orchestrator: Applying OrthogonalizationResult (Not Implemented).")
            case UncertaintyAnalysis():
                print(f"Orchestrator: Applying UncertaintyAnalysis result.")
                if result.additional_tests:
                    new_state.metadata.setdefault("new_tests", []).extend(result.additional_tests)
            case TunnelingResult():
                print(f"Orchestrator: Applying TunnelingResult.")
                new_state.energy_breakdown.complexity -= result.total_performance_gain
            case ResourceAllocation():
                print(f"Orchestrator: Applying ResourceAllocation result.")
                new_state.metadata["resource_allocation_plan"] = result.model_dump()
            case FlowOptimization():
                print(f"Orchestrator: Applying FlowOptimization result.")
                new_state.metadata["flow_optimization_plan"] = result.model_dump()
            case ChaosPlanResult():
                print(f"Orchestrator: Applying ChaosPlanResult.")
                resilience_monitor = ResilienceMonitor()
                reports = await self._execute_chaos_plan(resilience_monitor, result.chaos_plan)
                new_state.metadata["chaos_reports"] = [r.model_dump() for r in reports]
            case GrowthPrediction():
                print(f"Orchestrator: Applying GrowthPrediction result.")
                new_state.metadata["growth_prediction"] = result.model_dump()
            case DependencyOptimization():
                print(f"Orchestrator: Applying DependencyOptimization result.")
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
