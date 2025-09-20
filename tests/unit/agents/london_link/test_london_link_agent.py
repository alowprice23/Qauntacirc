import pytest
from unittest.mock import patch
from agents.london_link.agent import LondonLinkAgent
from core.types import (
    SystemState, DependencyGraph, Component, Dependency,
    EnergyBreakdown, LyapunovMetrics, SoftwareState, DependencyOptimization,
    DependencyOptimizationMove
)

@pytest.fixture
def london_link_agent():
    """Fixture for a LondonLinkAgent instance."""
    return LondonLinkAgent()

@pytest.fixture
def system_state_with_graph():
    """Fixture for a SystemState with a sample dependency graph."""
    nodes = [
        Component(id="a", properties={"polarizability": 0.5}),
        Component(id="b", properties={"polarizability": 0.8}),
        Component(id="c", properties={"polarizability": 0.3})
    ]
    edges = [
        Dependency(source=nodes[0].model_dump(), target=nodes[1].model_dump(), strength=0.7),
        Dependency(source=nodes[1].model_dump(), target=nodes[2].model_dump(), strength=0.4)
    ]
    graph = DependencyGraph(nodes=[n.model_dump() for n in nodes], edges=edges)

    state = SystemState(
        software_state=SoftwareState(),
        dependency_graph=graph,
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0)
    )
    return state

def test_apply_physics_principle_success(london_link_agent, system_state_with_graph):
    """
    Tests that apply_physics_principle correctly analyzes the dependency graph
    and proposes optimizations.
    """
    # Mock the optimizer to return a predictable result
    mock_move = DependencyOptimizationMove(
        description="Refactor module 'b' to reduce coupling with 'a'",
        potential_reduction=10.5
    )
    with patch.object(london_link_agent.dependency_optimizer, 'find_optimal_structure', return_value=[mock_move]):
        # Act
        result = london_link_agent.apply_physics_principle(system_state_with_graph)

        # Assert
        assert isinstance(result, DependencyOptimization)
        assert result.success is True
        assert result.agent_name == "london_link"
        assert result.physics_principle == "van der Waals Forces"

        # Check that the analysis was performed
        assert result.original_potential < 0  # van der Waals is attractive
        assert len(result.optimized_moves) == 1
        assert result.optimized_moves[0].description == mock_move.description
        assert result.expected_potential_reduction == 10.5

def test_apply_physics_principle_no_graph(london_link_agent):
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
    result = london_link_agent.apply_physics_principle(state)

    # Assert
    assert isinstance(result, DependencyOptimization)
    assert result.success is True # It's a successful analysis, just nothing to do
    assert result.original_potential == 0
    assert len(result.optimized_moves) == 0
