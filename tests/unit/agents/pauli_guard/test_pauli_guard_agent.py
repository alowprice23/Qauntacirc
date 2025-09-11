import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from agents.pauli_guard.agent import PauliGuardAgent
from core.types import QCState, AgentTask, SoftwareState, EnergyComponents

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    # Mock response for a cluster of 3
    mock_plan = {
        "shared_component_path": "src/shared/utils.py",
        "refactored_code": "def common_function():\n    # Shared logic for a, b, and c",
        "replacement_plan": [
            {
                "file_to_modify": "src/a.py",
                "original_code": "def f():...",
                "new_code": "from src.shared.utils import common_function\n\ndef f():\n    common_function()"
            },
            {
                "file_to_modify": "src/b.py",
                "original_code": "def g():...",
                "new_code": "from src.shared.utils import common_function\n\ndef g():\n    common_function()"
            },
            {
                "file_to_modify": "src/c.py",
                "original_code": "def h():...",
                "new_code": "from src.shared.utils import common_function\n\ndef h():\n    common_function()"
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
    # Set a low similarity threshold for testing purposes
    config = {"similarity_threshold": 0.7}
    return PauliGuardAgent(
        state_space=MagicMock(),
        energy_calculator=mock_energy_calculator,
        metrics_logger=MagicMock(),
        policy_engine=MagicMock(),
        agent_memory=MagicMock(),
        llm_client=mock_llm_client,
        config=config
    )

@pytest.fixture
def initial_state_with_duplicates():
    software_state = SoftwareState(component_versions={}, config_hashes={}, status="initial")
    energy_components = EnergyComponents(static=100.0, dynamic=50.0, interaction=30.0)
    return QCState(
        software_state=software_state,
        energy=energy_components.total,
        energy_components=energy_components,
        lyapunov_potential=180.0,
        contraction_factor=1.0,
        metadata={
            "schrodinger_dev_output": {
                "files_to_create": {
                    "src/a.py": "def f():\n    print(1)\n    print(2)\n    print(3)\n    print(4)\n    print(5)",
                    "src/b.py": "def g():\n    print(1)\n    print(2)\n    print(3)\n    print(4)\n    print(5)",
                    "src/c.py": "def h():\n    print(1)\n    print(2)\n    print(3)\n    print(4)\n    print(5)",
                    "src/d.py": "def i():\n    # This one is different\n    return 100",
                }
            }
        }
    )

@pytest.fixture
def initial_state_no_duplicates():
    software_state = SoftwareState(component_versions={}, config_hashes={}, status="initial")
    energy_components = EnergyComponents(static=100.0, dynamic=50.0, interaction=10.0)
    return QCState(
        software_state=software_state,
        energy=energy_components.total,
        energy_components=energy_components,
        lyapunov_potential=160.0,
        contraction_factor=1.0,
        metadata={
            "schrodinger_dev_output": {
                "files_to_create": {
                    "src/a.py": "def f():\n    return 1",
                    "src/b.py": "def g():\n    return 2",
                }
            }
        }
    )


@pytest.mark.asyncio
async def test_analyze_state_with_duplicates_cluster(pauli_agent, initial_state_with_duplicates):
    proposal = await pauli_agent.analyze_state(initial_state_with_duplicates)

    assert proposal.status == "SUCCESS"
    assert "refactoring_plans" in proposal.payload
    # Should find one cluster of 3 similar files
    assert len(proposal.payload["refactoring_plans"]) == 1
    assert len(proposal.payload["duplicates_found"]) == 1

    # Check the plan details
    plan = proposal.payload["refactoring_plans"][0]
    assert len(plan["replacement_plan"]) == 3
    assert plan["shared_component_path"] == "src/shared/utils.py"

    # Check that the LLM was called
    pauli_agent.llm_client.complete.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_state_no_duplicates(pauli_agent, initial_state_no_duplicates):
    proposal = await pauli_agent.analyze_state(initial_state_no_duplicates)
    assert proposal.status == "SUCCESS"
    assert "refactoring_plans" in proposal.payload
    assert len(proposal.payload["refactoring_plans"]) == 0
    assert len(proposal.payload["duplicates_found"]) == 0
    pauli_agent.llm_client.complete.assert_not_called()


def test_execute_with_cluster(pauli_agent):
    proposal = AgentTask(
        agent_name="pauli_guard",
        task_type="refactor",
        payload={
            "refactoring_plans": [{"plan": "A"}],
            "duplicates_found": [
                {
                    "type": "similar_cluster",
                    "files": ["a.py", "b.py"],
                    "blocks": ["a" * 10, "b" * 20]
                }
            ]
        },
    )
    action = pauli_agent.execute(proposal)
    assert action.status == "SUCCESS"
    assert "refactoring_plans" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["interaction"] < 0

    # Energy reduction should be proportional to 10 + 20 = 30
    # 30 * 0.1 = 3.0
    # So energy impact should be -3.0
    assert action.result["energy_impact"]["interaction"] == -3.0
