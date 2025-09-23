import pytest
import numpy as np
from core.state_space import StateSpace
from core.types import QCState, Module, DependencyGraph, Component, Dependency, SoftwareState, EnergyBreakdown, LyapunovMetrics
from datetime import datetime

def create_test_qc_state(modules, dependency_graph, failing_tests) -> QCState:
    return QCState(
        modules=modules,
        dependency_graph=dependency_graph,
        failing_tests=failing_tests,
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=0, complexity=0, coupling=0, constraint=0, debt=0),
        lyapunov_metrics=LyapunovMetrics(phi=0, energy=0, test_penalty=0, obligation_penalty=0),
    )

def test_composite_distance():
    space = StateSpace(dimension=2) # dimension is not used for composite metric

    # State A
    modules_a = [Module(id="a", name="a", code="def f(): return 1", normalized_ast=b"def f(): return 1", semantic_tokens=[], cyclomatic_complexity=1, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())]
    nodes_a = [Component(id="a")]
    edges_a = []
    graph_a = DependencyGraph(nodes=[n.model_dump() for n in nodes_a], edges=[e.model_dump() for e in edges_a])
    tests_a = ["test_1", "test_2"]
    state_a = create_test_qc_state(modules_a, graph_a, tests_a)

    # State B (different ast, graph, and one different test)
    modules_b = [Module(id="a", name="a", code="def f(): return 2", normalized_ast=b"def f(): return 2", semantic_tokens=[], cyclomatic_complexity=1, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())]
    nodes_b = [Component(id="a"), Component(id="b")]
    edges_b = [Dependency(source=Component(id="a").model_dump(), target=Component(id="b").model_dump(), strength=1.0)]
    graph_b = DependencyGraph(nodes=[n.model_dump() for n in nodes_b], edges=[e.model_dump() for e in edges_b])
    tests_b = ["test_1", "test_3"]
    state_b = create_test_qc_state(modules_b, graph_b, tests_b)

    distance = space.compute_distance(state_a, state_b, metric='composite')
    assert distance > 0

    # Identical states should have zero distance
    distance_same = space.compute_distance(state_a, state_a, metric='composite')
    assert np.isclose(distance_same, 0.0)
