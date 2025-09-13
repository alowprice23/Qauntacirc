import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.london_link.agent import LondonLinkAgent
from core.data_models import (
    SystemState, AgentTask, EnergyBreakdown, LyapunovMetrics, Status,
    DependencyGraph, Component, Dependency, SoftwareState
)
from datetime import datetime

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {
        "content": '{"refactored_module_path": "src/a.py", "refactored_code": "new code", "explanation": "did a thing"}'
    }
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    return calculator

@pytest.fixture
def london_link_agent(mock_llm_client, mock_energy_calculator):
    return LondonLinkAgent(
        state_space=MagicMock(),
        energy_calculator=mock_energy_calculator,
        metrics_logger=MagicMock(),
        policy_engine=MagicMock(),
        agent_memory=MagicMock(),
        llm_client=mock_llm_client
    )

@pytest.fixture
def initial_state():
    """A state with three files forming a chain dependency A -> B -> C."""
    energy_breakdown = EnergyBreakdown(total=170.0, complexity=100.0, coupling=50.0, constraint=20.0, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=170.0, energy=170.0, test_penalty=0.0, obligation_penalty=0.0)

    nodes = [Component(id="a.py"), Component(id="b.py"), Component(id="c.py")]
    edges = [
        Dependency(source=nodes[0].model_dump(), target=nodes[1].model_dump(), strength=0.8),
        Dependency(source=nodes[1].model_dump(), target=nodes[2].model_dump(), strength=0.8)
    ]
    dep_graph = DependencyGraph(nodes=[n.model_dump() for n in nodes], edges=edges)

    return SystemState(
        software_state=SoftwareState(),
        dependency_graph=dep_graph,
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
    )

@pytest.mark.asyncio
async def test_analyze_state_finds_most_attractive_pair(london_link_agent, initial_state):
    proposal = london_link_agent.analyze_state(initial_state)
    assert proposal.status == Status.SUCCESS
    assert "dependency_optimization" in proposal.payload
    opt = proposal.payload["dependency_optimization"]
    assert "original_potential" in opt
    assert opt["original_potential"] < 0

def test_execute_calculates_energy_impact(london_link_agent):
    proposal = AgentTask(
        agent_name="london_link",
        task_type="dependency_optimization",
        payload={
            "dependency_optimization": {"original_potential": -100.0}
        },
        status=Status.SUCCESS
    )
    action = london_link_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert "dependency_optimization" in action.result
