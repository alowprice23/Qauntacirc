import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.tunnelfix.agent import TunnelFixAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

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
                    "src/a.py": "a = []\nfor i in range(10):\n    a.append(i*i)"
                }
            }
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_success(tunnelfix_agent, initial_state):
    # Mock the benchmark to return deterministic values, ensuring perf_improvement > 0
    tunnelfix_agent.benchmark = MagicMock()
    tunnelfix_agent.benchmark.run.side_effect = [
        0.02,  # Baseline performance
        0.01   # Optimized performance
    ]

    proposal = await tunnelfix_agent.analyze_state(initial_state)

    assert proposal.status == "SUCCESS"
    assert "optimizations" in proposal.payload
    assert len(proposal.payload["optimizations"]) == 1, "Should find exactly one optimization"

    opt_key = list(proposal.payload["optimizations"].keys())[0]
    assert opt_key == "src/a.py"

    opt_data = proposal.payload["optimizations"][opt_key]
    assert opt_data["performance_improvement"] == pytest.approx(0.01)
    assert "tunneling_probability" in opt_data
    assert 0 <= opt_data["tunneling_probability"] <= 1.0

def test_execute(tunnelfix_agent):
    proposal = AgentTask(
        agent_name="tunnelfix",
        task_type="optimization",
        payload={
            "optimizations": {
                "src/a.py": {
                    "performance_improvement": 0.01,
                    "tunneling_probability": 0.5
                }
            }
        },
    )
    action = tunnelfix_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "optimizations" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["debt"] < 0
