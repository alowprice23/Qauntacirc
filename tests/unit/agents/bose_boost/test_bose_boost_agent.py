import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.bose_boost.agent import BoseBoostAgent
from core.types import SystemState, AgentTask, EnergyBreakdown, LyapunovMetrics, Status, Module, SoftwareState
from datetime import datetime

@pytest.fixture
def mock_llm_client():
    return AsyncMock()

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_replicas": 1.0}
    return calculator

@pytest.fixture
def bose_agent(mock_llm_client, mock_energy_calculator):
    return BoseBoostAgent(
        state_space=MagicMock(),
        energy_calculator=mock_energy_calculator,
        metrics_logger=MagicMock(),
        policy_engine=MagicMock(),
        agent_memory=MagicMock(),
        llm_client=mock_llm_client
    )

@pytest.fixture
def initial_state():
    energy_breakdown = EnergyBreakdown(total=170.0, complexity=100.0, coupling=50.0, constraint=20.0, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=170.0, energy=170.0, test_penalty=0.0, obligation_penalty=0.0)
    modules = [
        Module(name="task1", normalized_ast=b"", semantic_tokens=[], cyclomatic_complexity=20.0, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now()),
        Module(name="task2", normalized_ast=b"", semantic_tokens=[], cyclomatic_complexity=80.0, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())
    ]
    return SystemState(
        software_state=SoftwareState(),
        modules=modules,
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
    )

@pytest.mark.asyncio
async def test_analyze_state_success(bose_agent, initial_state):
    proposal = bose_agent.analyze_state(initial_state)
    assert proposal.status == Status.SUCCESS
    assert "resource_allocation" in proposal.payload
    allocation = proposal.payload["resource_allocation"]
    assert "task1" in allocation["allocations"]
    assert "task2" in allocation["allocations"]

def test_execute(bose_agent):
    proposal = AgentTask(
        agent_name="bose_boost",
        task_type="scaling",
        payload={
            "resource_allocation": {"allocations": {"task1": {"replicas": 2}}}
        },
        status=Status.SUCCESS
    )
    action = bose_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert "resource_allocation" in action.result
