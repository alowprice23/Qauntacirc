import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.uncertain_ai.agent import UncertainAIAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    # Mock response for risk identification
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
    software_state = SoftwareState(component_versions={}, config_hashes={}, status="initial")
    energy_components = EnergyComponents(static=100.0, dynamic=50.0, interaction=20.0)
    return QCState(
        software_state=software_state,
        energy=energy_components.total,
        energy_components=energy_components,
        lyapunov_potential=170.0,
        contraction_factor=1.0,
        metadata={
            "schrodinger_dev_output": {
                "files_to_create": {
                    "src/a.py": "def f(): pass"
                }
            }
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_success(uncertain_agent, initial_state):
    proposal = await uncertain_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "newly_generated_tests" in proposal.payload
    assert len(proposal.payload["newly_generated_tests"]) == 2
    assert "total_uncertainty_reduction" in proposal.payload
    assert proposal.payload["total_uncertainty_reduction"] > 0

def test_execute(uncertain_agent):
    proposal = AgentTask(
        agent_name="uncertain_ai",
        task_type="analysis",
        payload={
            "newly_generated_tests": ["test1", "test2"],
            "total_uncertainty_reduction": 0.5
        },
    )
    action = uncertain_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "new_test_cases" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["dynamic"] == pytest.approx(-5.0)
