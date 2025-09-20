import pytest
from agents.phonon_flow.agent import PhononFlowAgent
from core.types import (
    SystemState, DependencyGraph, Component, Dependency,
    EnergyBreakdown, LyapunovMetrics, SoftwareState, FlowOptimization
)

@pytest.fixture
def phonon_agent():
    """Fixture for a PhononFlowAgent instance."""
    return PhononFlowAgent()

@pytest.fixture
def system_state_with_graph():
    """Fixture for a SystemState with a sample dependency graph for flow analysis."""
    nodes = [
        Component(id="a"),
        Component(id="b"),
        Component(id="c")
    ]
    edges = [
        Dependency(source=nodes[0].model_dump(), target=nodes[1].model_dump(), strength=0.9), # Strong bond -> high freq
        Dependency(source=nodes[1].model_dump(), target=nodes[2].model_dump(), strength=0.2)  # Weak bond -> low freq
    ]
    graph = DependencyGraph(nodes=[n.model_dump() for n in nodes], edges=edges)

    state = SystemState(
        software_state=SoftwareState(),
        dependency_graph=graph,
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0)
    )
    return state

def test_apply_physics_principle_success(phonon_agent, system_state_with_graph):
    """
    Tests that apply_physics_principle correctly analyzes communication flow
    and proposes optimizations.
    """
    # Act
    result = phonon_agent.apply_physics_principle(system_state_with_graph)

    # Assert
    assert isinstance(result, FlowOptimization)
    assert result.success is True
    assert result.agent_name == "phonon_flow"
    assert result.physics_principle == "Lattice Dynamics"

    # Check that analysis was performed
    assert len(result.dispersion_relations) > 0
    assert len(result.optimized_channels) > 0
    assert result.total_bandwidth > 0
    assert "latency_improvement" in result.model_dump()

def test_apply_physics_principle_no_graph(phonon_agent):
    """
    Tests that the agent handles a system state with no dependency graph.
    """
    state = SystemState(
        software_state=SoftwareState(),
        dependency_graph=None,
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0)
    )

    # Act
    result = phonon_agent.apply_physics_principle(state)

    # Assert
    assert isinstance(result, FlowOptimization)
    assert result.success is True # Successful analysis, just nothing to do
    assert result.total_bandwidth == 0
    assert result.latency_improvement == 0
    assert len(result.optimized_channels) == 0
