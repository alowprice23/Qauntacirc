import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from agents.pauli_guard.agent import PauliGuardAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    # A more realistic mock response for the refactoring plan
    mock_plan = {
        "shared_component_path": "src/shared_logic.py",
        "refactored_code": "def common_function():\n    print(1)\n    print(2)\n    print(3)\n    print(4)\n    print(5)",
        "replacement_plan": [
            {
                "file_path": "src/a.py",
                "original_block": "def f():...",
                "replacement_code": "from src.shared_logic import common_function\n\ndef f():\n    common_function()"
            },
            {
                "file_path": "src/b.py",
                "original_block": "def g():...",
                "replacement_code": "from src.shared_logic import common_function\n\ndef g():\n    common_function()"
            }
        ]
    }
    client.complete.return_value = {"content": json.dumps(mock_plan)}
    return client

@pytest.fixture
def mock_energy_calculator():
    calculator = MagicMock()
    calculator.config = {"w_coupling_reduction": 0.1}
    return calculator

@pytest.fixture
def pauli_agent(mock_llm_client, mock_energy_calculator):
    return PauliGuardAgent(
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
                    "src/a.py": "def f():\n    print(1)\n    print(2)\n    print(3)\n    print(4)\n    print(5)",
                    "src/b.py": "def g():\n    print(1)\n    print(2)\n    print(3)\n    print(4)\n    print(5)",
                }
            }
        }
    )

@pytest.mark.asyncio
async def test_analyze_state_with_duplicates(pauli_agent, initial_state):
    proposal = await pauli_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "refactoring_plans" in proposal.payload
    assert len(proposal.payload["refactoring_plans"]) > 0

@pytest.mark.asyncio
async def test_analyze_state_no_duplicates(pauli_agent, initial_state):
    initial_state.metadata["schrodinger_dev_output"]["files_to_create"] = {"src/a.py": "def f(): pass", "src/b.py": "def g(): pass"}
    proposal = await pauli_agent.analyze_state(initial_state)
    assert proposal.status == "SUCCESS"
    assert "refactoring_plans" in proposal.payload
    assert len(proposal.payload["refactoring_plans"]) == 0

def test_execute(pauli_agent):
    proposal = AgentTask(
        agent_name="pauli_guard",
        task_type="refactor",
        payload={
            "refactoring_plans": [{"plan": "A"}],
            "duplicates_found": [{"block_1": {"content": "a" * 10}, "block_2": {"content": "a" * 10}}]
        },
    )
    action = pauli_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "refactoring_plans" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["interaction"] < 0
