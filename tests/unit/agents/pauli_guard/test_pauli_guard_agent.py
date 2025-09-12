import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from agents.pauli_guard.agent import PauliGuardAgent
from core.types import SystemState, AgentTask, EnergyBreakdown, LyapunovMetrics, Status, Module, SoftwareState
from datetime import datetime

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    mock_plan = {
        "shared_component_path": "src/shared/utils.py",
        "refactored_code": "def common_function():\n    # Shared logic for a, b, and c",
        "replacement_plan": [
            {"file_to_modify": "src/a.py", "original_code": "def f():...", "new_code": "..."},
            {"file_to_modify": "src/b.py", "original_code": "def g():...", "new_code": "..."},
            {"file_to_modify": "src/c.py", "original_code": "def h():...", "new_code": "..."}
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

def create_mock_module(name, content):
    return Module(
        name=name,
        normalized_ast=content.encode(),
        semantic_tokens=[],
        cyclomatic_complexity=1,
        duplication_factor=0,
        coverage_deficit=0,
        last_refactor=datetime.now()
    )

@pytest.fixture
def initial_state_with_duplicates():
    energy_breakdown = EnergyBreakdown(total=180.0, complexity=100.0, coupling=50.0, constraint=30.0, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=180.0, energy=180.0, test_penalty=0.0, obligation_penalty=0.0)
    files = {
        "src/a.py": "def f():\n    print(1)\n    print(2)\n    print(3)\n    print(4)\n    print(5)",
        "src/b.py": "def g():\n    print(1)\n    print(2)\n    print(3)\n    print(4)\n    print(5)",
        "src/c.py": "def h():\n    print(1)\n    print(2)\n    print(3)\n    print(4)\n    print(5)",
        "src/d.py": "def i():\n    # This one is different\n    return 100",
    }
    modules = [create_mock_module(name, content) for name, content in files.items()]
    return SystemState(
        software_state=SoftwareState(),
        modules=modules,
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
        metadata={"schrodinger_dev_output": {"files_to_create": files}}
    )

@pytest.fixture
def initial_state_no_duplicates():
    energy_breakdown = EnergyBreakdown(total=160.0, complexity=100.0, coupling=50.0, constraint=10.0, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=160.0, energy=160.0, test_penalty=0.0, obligation_penalty=0.0)
    files = {
        "src/a.py": "def f():\n    return 1",
        "src/b.py": "def g():\n    return 2",
    }
    modules = [create_mock_module(name, content) for name, content in files.items()]
    return SystemState(
        software_state=SoftwareState(),
        modules=modules,
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
        metadata={"schrodinger_dev_output": {"files_to_create": files}}
    )


@pytest.mark.asyncio
async def test_analyze_state_with_duplicates_cluster(pauli_agent, initial_state_with_duplicates):
    proposal = pauli_agent.analyze_state(initial_state_with_duplicates)
    assert proposal.status == "SUCCESS"
    assert "refactoring_plans" in proposal.payload
    assert len(proposal.payload["refactoring_plans"]) == 1
    assert len(proposal.payload["duplicates_found"]) > 0

@pytest.mark.asyncio
async def test_analyze_state_no_duplicates(pauli_agent, initial_state_no_duplicates):
    proposal = pauli_agent.analyze_state(initial_state_no_duplicates)
    assert proposal.status == "SUCCESS"
    assert "refactoring_plans" in proposal.payload
    assert len(proposal.payload["refactoring_plans"]) == 0
    assert len(proposal.payload["duplicates_found"]) == 0

def test_execute_with_cluster(pauli_agent):
    proposal = AgentTask(
        agent_name="pauli_guard",
        task_type="refactor",
        payload={
            "refactoring_plans": [{"plan": "A"}],
            "duplicates_found": [
                { "type": "similar_cluster", "files": ["a.py", "b.py"], "blocks": ["a" * 10, "b" * 20] }
            ]
        },
        status=Status.SUCCESS
    )
    action = pauli_agent.execute(proposal)
    assert action.status == Status.SUCCESS
    assert "refactoring_plans" in action.result
    assert "energy_impact" in action.result
    assert action.result["energy_impact"]["interaction"] < 0
    assert action.result["energy_impact"]["interaction"] == -3.0
