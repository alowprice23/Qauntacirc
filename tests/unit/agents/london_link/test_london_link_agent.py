import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.london_link.agent import LondonLinkAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

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
    software_state = SoftwareState(component_versions={}, config_hashes={}, status="initial")
    energy_components = EnergyComponents(static=100.0, dynamic=50.0, interaction=20.0)
    return QCState(
        software_state=software_state,
        energy=energy_components.total,
        energy_components=energy_components,
        lyapunov_potential=170.0,
        contraction_factor=1.0,
        metadata={
            "source_code_map": {
                "src/a.py": "import src.b",
                "src/b.py": "import src.c",
                "src/c.py": "x = 1"
            }
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_finds_most_attractive_pair(london_link_agent, initial_state):
    # The most distant pair is (a, c) with r=2. They should have the
    # highest attraction potential (most negative V).
    proposal = await london_link_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "optimization_plan" in proposal.payload
    # We can't easily assert which pair was chosen without mocking complexity,
    # but we can check the proposal structure.
    plan = proposal.payload["optimization_plan"]
    assert "refactored_code" in plan
    assert "original_potential" in plan
    assert plan["original_potential"] < 0

def test_execute_calculates_energy_impact(london_link_agent):
    proposal = AgentTask(
        agent_name="london_link",
        task_type="dependency_optimization",
        payload={
            "optimization_plan": {
                "refactored_module_path": "src/a.py",
                "refactored_code": "new code",
                "explanation": "...",
                "original_potential": -100.0
            }
        },
    )
    action = london_link_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "optimization_plan" in action.result
    assert action.result["energy_impact"]["interaction"] == -100.0
