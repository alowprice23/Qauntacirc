import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.uncertain_ai.agent import UncertainAIAgent
from core.data_models import SystemState, AgentTask, EnergyBreakdown, LyapunovMetrics, Status, Module, SoftwareState
from datetime import datetime

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.side_effect = [
        {"content": '{"identified_risks": ["risk1", "risk2"]}'},
        {"content": "```python\nimport unittest\nclass Test1(unittest.TestCase):\n    def test_risk1(self): self.assertTrue(True)\n```"},
        {"content": "```python\nimport unittest\nclass Test2(unittest.TestCase):\n    def test_risk2(self): self.assertTrue(True)\n```"},
    ]
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_uncertainty": 10.0}
    return calculator

@pytest.fixture
def uncertain_agent(mock_llm_client, mock_energy_calculator):
    return UncertainAIAgent(
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
        Module(name="a.py", normalized_ast=b"", semantic_tokens=[], cyclomatic_complexity=5, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())
    ]
    requirements = ["req1", "req2"]
    return SystemState(
        software_state=SoftwareState(),
        modules=modules,
        requirements=requirements,
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
    )

@pytest.mark.asyncio
async def test_analyze_state_success(uncertain_agent, initial_state):
    proposal = uncertain_agent.analyze_state(initial_state)
    assert proposal.status == Status.SUCCESS
    assert "uncertainty_analysis" in proposal.payload
    analysis = proposal.payload["uncertainty_analysis"]
    assert "spec_uncertainty" in analysis
    assert "impl_uncertainty" in analysis

def test_execute(uncertain_agent):
    proposal = AgentTask(
        agent_name="uncertain_ai",
        task_type="analysis",
        payload={
            "uncertainty_analysis": {
                "spec_uncertainty": 0.1, "impl_uncertainty": 0.2, "uncertainty_product": 0.02,
                "satisfies_principle": False, "additional_tests": [], "risk_bounds": {"lower_bound":0, "upper_bound":1, "confidence":0.95}
            }
        },
        status=Status.SUCCESS
    )
    action = uncertain_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert "uncertainty_analysis" in action.result
