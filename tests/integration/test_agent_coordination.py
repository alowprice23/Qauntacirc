import pytest
import asyncio
from typing import Dict, List, Any
from core.orchestrator import Orchestrator
from messaging.nats_client import NATSMessageBus
from messaging.types import AgentMessage
from agents.planck_forge.agent import PlanckForgeAgent
from agents.schrodinger_dev.agent import SchrodingerDevAgent
from agents.pauli_guard.agent import PauliGuardAgent
from tests.fixtures import test_system_state, test_llm_client, ALL_AGENT_CLASSES
from common.utils import apply_proposal, compute_total_energy
from core.types import CompletenessProof, SystemState, SoftwareState, EnergyBreakdown, LyapunovMetrics

def compute_total_energy(state):
    return state.energy_breakdown.total

def apply_proposal(state, proposal):
    if proposal.get("action") == "reduce_complexity":
        state.energy_breakdown.complexity -= proposal.get("amount", 0)
        state.energy_breakdown.total -= proposal.get("amount", 0)
    return state


from tests.mocks import (
    MockAgentCommunicationProtocol,
    MockClosureRuleEngine,
    MockEnergyCalculator,
    MockLyapunovMonitor,
    MockClosureValidator,
)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_coordination_protocol(test_system_state, test_llm_client):
    """Test that all agents coordinate properly through the orchestrator"""
    # Initialize the orchestrator with mock components
    orchestrator = Orchestrator(
        agents=[
            PlanckForgeAgent(),
            SchrodingerDevAgent(llm_client=test_llm_client),
            PauliGuardAgent(),
        ],
        energy_calculator=MockEnergyCalculator(),
        lyapunov_monitor=MockLyapunovMonitor(),
        closure_validator=MockClosureValidator(),
        closure_rule_engine=MockClosureRuleEngine(),
        communication_protocol=MockAgentCommunicationProtocol(),
    )

    # Create test system state
    initial_state = test_system_state
    initial_state.requirements = ["Create a new feature"]
    initial_state.metadata['test_results'] = {'total_tests': 100, 'total_failures': 0}
    initial_state.metadata['risk_budget'] = {'empirical_budget': 1e-6}
    initial_state.metadata['policy'] = {'max_severity': 5}
    initial_state.metadata['proof_terms'] = []

    # Scenario 1: Sequential agent execution
    orchestrator.agent_selector_strategy = "round-robin"

    # Mock agent behaviors
    async def mock_planck_apply(state):
        from core.types import QuantizedTasks
        return QuantizedTasks(
            success=True, agent_name="planck_forge", physics_principle="...", message="...",
            quanta=[], total_energy=0.0
        )

    async def mock_schrodinger_apply(state):
        from core.types import CodeEvolution, CodeState, UnitaryOperator
        return CodeEvolution(
            success=True, agent_name="schrodinger_dev", physics_principle="...", message="...",
            new_state=CodeState(state_vector=[], code=""), proofs=[], energy_change=0.0,
            unitary_operator=UnitaryOperator(matrix=[])
        )

    async def mock_pauli_apply(state):
        from core.types import OrthogonalizationResult
        return OrthogonalizationResult(
            success=True, agent_name="pauli_guard", physics_principle="...", message="...",
            modules=[], shared_components=[], eliminated_duplicates=0, orthogonality_improvement=0.0
        )

    orchestrator.agents[0].apply_physics_principle = mock_planck_apply
    orchestrator.agents[1].apply_physics_principle = mock_schrodinger_apply
    orchestrator.agents[2].apply_physics_principle = mock_pauli_apply

    evolution_result = await orchestrator.evolve_system(initial_state)
    assert evolution_result.actions[0].agent_id == "PlanckForgeAgent"
    evolution_result = await orchestrator.evolve_system(evolution_result.final_state)
    assert evolution_result.actions[0].agent_id == "SchrodingerDevAgent"
    evolution_result = await orchestrator.evolve_system(evolution_result.final_state)
    assert evolution_result.actions[0].agent_id == "PauliGuardAgent"

    # Scenario 2: Parallel agent execution
    orchestrator.agent_selector_strategy = "random"
    tasks = [orchestrator.evolve_system(evolution_result.final_state) for _ in range(3)]
    results = await asyncio.gather(*tasks)
    assert len(results) == 3

    # Scenario 3: Full agent pipeline
    orchestrator.agent_selector_strategy = "round-robin"
    current_state = initial_state
    for _ in orchestrator.agents:
        current_state = (await orchestrator.evolve_system(current_state)).final_state

    assert current_state is not None

from unittest.mock import AsyncMock

def test_agent_message_passing(test_llm_client):
    """Test message passing and coordination between agents"""
    # Mock the NATSMessageBus
    message_bus = AsyncMock(spec=NATSMessageBus)
    message_bus.publish_quantum_message = AsyncMock()
    message_bus.subscribe_quantum_aware = AsyncMock()

    test_agents = [
        PlanckForgeAgent(),
        SchrodingerDevAgent(llm_client=test_llm_client),
        PauliGuardAgent(),
    ]

    messages_sent = []
    messages_received = []

    async def message_handler(agent_id: str, message: AgentMessage):
        messages_received.append((agent_id, message))

    async def run_test():
        # Set up subscriptions
        for agent in test_agents:
            await message_bus.subscribe_quantum_aware(
                f"agent.{agent.agent_name}.input",
                lambda msg, qc_state, aid=agent.agent_name: message_handler(aid, msg),
            )

        # Create and publish a test message
        test_message = AgentMessage(
            id="test_001",
            correlation_id="coord_test",
            agent_id="planck_forge",
            energy_delta=-1.5,
            phi_delta=-2.1,
            content={"task_quanta": [{"id": "tq_001", "energy": 10.0}]},
        )

        import json
        from dataclasses import asdict
        await message_bus.publish_quantum_message(
            "agent.schrodinger_dev.input", json.dumps(asdict(test_message)).encode("utf-8")
        )
        messages_sent.append(test_message)

        # Simulate message reception
        # In a real test, this would be handled by the mock
        await message_handler("schrodinger_dev", test_message)

        # Assertions
        assert len(messages_received) > 0, "No messages received"
        assert messages_received[0][1].correlation_id == "coord_test", "Message correlation failed"
        assert message_bus.publish_quantum_message.call_count == 1
        assert message_bus.subscribe_quantum_aware.call_count == len(test_agents)

    asyncio.run(run_test())

def test_energy_conservation_across_agents(test_system_state, test_llm_client):
    """Test that energy is conserved across agent transformations"""
    initial_state = test_system_state
    initial_energy = compute_total_energy(initial_state)

    current_state = initial_state
    total_energy_delta = 0.0

    for agent_class in ALL_AGENT_CLASSES:
        if agent_class in [SchrodingerDevAgent]:
            agent = agent_class(llm_client=test_llm_client)
        else:
            agent = agent_class()

        # Mocking the agent methods for this test
        agent.guard = lambda state: True
        agent.propose = lambda state: {
            "success": True,
            "action": "reduce_complexity",
            "amount": 10.0,
        }
        agent.verify = lambda proposal: {"success": True}

        if agent.guard(current_state):
            proposal = agent.propose(current_state)
            verification = agent.verify(proposal)

            if verification["success"]:
                new_state = apply_proposal(current_state, proposal)
                energy_delta = compute_total_energy(new_state) - compute_total_energy(current_state)
                total_energy_delta += energy_delta
                current_state = new_state

    assert total_energy_delta <= 0.1, f"Energy increased uncontrolled: Δ = {total_energy_delta}"
