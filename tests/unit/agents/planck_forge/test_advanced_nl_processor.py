import pytest
from unittest.mock import MagicMock, AsyncMock

from agents.planck_forge.advanced_nl_processor import (
    AdvancedQuantumNLProcessor,
    SemanticWorkflowDecomposer,
    CommandDependencyAnalyzer,
    PhysicsGuidedParser,
    SessionContext,
    DecompositionResult,
    DependencyAnalysisResult,
    ExecutionPlan,
)
from core.types import TaskQuanta, DependencyGraph, SystemState, EnergyBreakdown, LyapunovMetrics, Component, Dependency
from llm.client import LLMClient

@pytest.fixture
def mock_llm_client():
    client = MagicMock(spec=LLMClient)
    # Mock the synchronous complete method
    client.complete = MagicMock()
    return client

@pytest.fixture
def sample_system_state():
    return SystemState(
        software_state=MagicMock(),
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=10.0, debt=10.0),
        lyapunov_metrics=LyapunovMetrics(phi=120.0, energy=100.0, test_penalty=10.0, obligation_penalty=10.0)
    )

@pytest.mark.asyncio
async def test_semantic_workflow_decomposer(mock_llm_client):
    # Arrange
    decomposer = SemanticWorkflowDecomposer(mock_llm_client)
    complex_command = "test command"

    # Mock LLM responses
    goals_response = {"response": '{"goals": ["goal1", "goal2"]}'}
    tasks_response1 = {"response": '{"tasks": [{"task_id": "T1", "description": "task1", "dependencies": [], "verification_criteria": ["vc1"]}]}'}
    tasks_response2 = {"response": '{"tasks": [{"task_id": "T2", "description": "task2", "dependencies": ["T1"], "verification_criteria": ["vc2"]}]}'}
    mock_llm_client.complete.side_effect = [goals_response, tasks_response1, tasks_response2]

    # Act
    result = await decomposer.decompose_with_physics(complex_command)

    # Assert
    assert len(result.goals) == 2
    assert len(result.atomic_operations) == 2
    assert result.atomic_operations[0].description == "task1"
    assert result.atomic_operations[1].id == "T02" # Check re-indexing

def test_command_dependency_analyzer():
    # Arrange
    analyzer = CommandDependencyAnalyzer()
    tasks = [
        TaskQuanta(task_id="T01", description="task1", dependencies=[], verification_criteria=["vc1"]),
        TaskQuanta(task_id="T02", description="task2", dependencies=["T01"], verification_criteria=["vc2"]),
    ]

    # Act
    result = analyzer.analyze_dependencies(tasks)

    # Assert
    assert isinstance(result.dependency_graph, DependencyGraph)
    assert len(result.dependency_graph.nodes) == 2
    assert len(result.dependency_graph.edges) == 1
    assert result.dependency_graph.edges[0].source.id == "T01"
    assert result.dependency_graph.edges[0].target.id == "T02"

def test_physics_guided_parser():
    # Arrange
    parser = PhysicsGuidedParser()
    tasks = [
        TaskQuanta(task_id="T01", description="task1", dependencies=[], verification_criteria=["vc1"], energy=10.0),
        TaskQuanta(task_id="T02", description="task2", dependencies=[], verification_criteria=["vc2"], energy=5.0),
        TaskQuanta(task_id="T03", description="task3", dependencies=["T01", "T02"], verification_criteria=["vc3"], energy=20.0),
    ]
    nodes = [Component(id=t.id, properties=t.model_dump()) for t in tasks]
    edges = [
        Dependency(source=nodes[0].model_dump(), target=nodes[2].model_dump(), strength=1.0),
        Dependency(source=nodes[1].model_dump(), target=nodes[2].model_dump(), strength=1.0),
    ]
    dep_graph = DependencyGraph(
        nodes=[node.model_dump() for node in nodes],
        edges=[edge.model_dump() for edge in edges]
    )

    # Act
    result = parser.create_optimal_plan(tasks, dep_graph, 100.0)

    # Assert
    assert isinstance(result, ExecutionPlan)
    assert len(result.optimal_order) == 3
    # T02 should come before T01 because it has lower energy
    assert result.optimal_order[0].id == "T02"
    assert result.optimal_order[1].id == "T01"
    assert result.optimal_order[2].id == "T03"
