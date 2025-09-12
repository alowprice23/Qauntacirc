import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.tunnel_fix.agent import TunnelFixAgent
from core.types import SystemState, AgentTask, EnergyBreakdown, LyapunovMetrics, Status, Module, PerformanceProfile, SoftwareState
from datetime import datetime

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {"content": '{"refactored_code": "b = [i*i for i in range(10)]"}'}
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_performance": 100.0}
    return calculator

@pytest.fixture
def tunnelfix_agent(mock_llm_client, mock_energy_calculator):
    return TunnelFixAgent(
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
        Module(name="a.py", normalized_ast=b"a = []\nfor i in range(10):\n    a.append(i*i)", semantic_tokens=[], cyclomatic_complexity=2, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())
    ]
    return SystemState(
        software_state=SoftwareState(),
        modules=modules,
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
        total_complexity=sum(m.cyclomatic_complexity for m in modules)
    )

@pytest.mark.asyncio
async def test_analyze_state_success(tunnelfix_agent, initial_state):
    proposal = tunnelfix_agent.analyze_state(initial_state)
    assert proposal.status == Status.SUCCESS
    assert "tunneling_result" in proposal.payload
    result = proposal.payload["tunneling_result"]
    assert result["barriers_detected"] > 0
    assert result["tunneling_opportunities"] > 0

def test_execute(tunnelfix_agent):
    proposal = AgentTask(
        agent_name="tunnelfix",
        task_type="optimization",
        payload={
            "tunneling_result": {
                "barriers_detected": 1,
                "tunneling_opportunities": 1,
                "applied_optimizations": [],
                "total_performance_gain": 0.0
            }
        },
        status=Status.SUCCESS
    )
    action = tunnelfix_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert "tunneling_result" in action.result
