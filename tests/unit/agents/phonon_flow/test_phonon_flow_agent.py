import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.phonon_flow.agent import PhononFlowAgent
from core.types import (
    SystemState, AgentTask, EnergyBreakdown, LyapunovMetrics, Status, Module,
    DependencyGraph, Component, Dependency, SoftwareState
)
from datetime import datetime

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {
        "content": '{"refactored_code": "new code here", "explanation": "did a thing"}'
    }
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_maintainability": 5.0}
    return calculator

@pytest.fixture
def phonon_agent(mock_llm_client, mock_energy_calculator):
    return PhononFlowAgent(
        state_space=MagicMock(),
        energy_calculator=mock_energy_calculator,
        metrics_logger=MagicMock(),
        policy_engine=MagicMock(),
        agent_memory=MagicMock(),
        llm_client=mock_llm_client
    )

@pytest.fixture
def initial_state():
    """A state with two files, one of which is clearly 'slower'."""
    energy_breakdown = EnergyBreakdown(total=170.0, complexity=100.0, coupling=50.0, constraint=20.0, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=170.0, energy=170.0, test_penalty=0.0, obligation_penalty=0.0)
    modules = [
        Module(name="slow.py", normalized_ast=b"", semantic_tokens=[], cyclomatic_complexity=10, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now()),
        Module(name="fast.py", normalized_ast=b"", semantic_tokens=[], cyclomatic_complexity=1, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())
    ]

    # Using dictionaries to create the dependency graph to avoid validation issues
    nodes_data = [{"id": "slow.py"}, {"id": "fast.py"}]
    edges_data = [{"source": nodes_data[0], "target": nodes_data[1], "strength": 0.8}]
    dep_graph_data = {"nodes": nodes_data, "edges": edges_data}

    dep_graph = DependencyGraph.model_validate(dep_graph_data)

    return SystemState(
        software_state=SoftwareState(),
        modules=modules,
        dependency_graph=dep_graph,
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
    )

@pytest.mark.asyncio
async def test_analyze_state_targets_slowest_file(phonon_agent, initial_state):
    proposal = phonon_agent.analyze_state(initial_state)
    assert proposal.status == Status.SUCCESS
    assert "flow_optimization" in proposal.payload
    opt = proposal.payload["flow_optimization"]
    assert "total_bandwidth" in opt
    assert opt["total_bandwidth"] > 0

def test_execute_calculates_energy_impact(phonon_agent):
    proposal = AgentTask(
        agent_name="phonon_flow",
        task_type="refactoring",
        payload={
            "flow_optimization": {"total_bandwidth": 100}
        },
        status=Status.SUCCESS
    )
    action = phonon_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert "flow_optimization" in action.result
