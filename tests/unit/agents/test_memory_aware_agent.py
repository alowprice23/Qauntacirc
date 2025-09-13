import pytest
from unittest.mock import MagicMock
import numpy as np

from agents.memory_aware_agent import MemoryAwareAgent
from memory.constellation import ConstellationMemory
from core.types import SystemState, AgentAction, SoftwareState, EnergyBreakdown, LyapunovMetrics
from memory.contracts import ActionResult
from memory.types import ConstellationConfig, Fact, FactNode, OptimalEncoding, FactType

@pytest.fixture
def mock_constellation():
    """Provides a mocked ConstellationMemory instance."""
    config = ConstellationConfig(
        neo4j_uri="bolt://localhost:7687",
        embedding_dimension=4,
        database_path=":memory:"
    )
    constellation = MagicMock(spec=ConstellationMemory)
    return constellation

@pytest.fixture
def memory_agent(mock_constellation):
    """Provides a MemoryAwareAgent instance with a mocked constellation."""
    return MemoryAwareAgent(agent_type="test_agent", constellation=mock_constellation)

@pytest.fixture
def valid_system_state():
    """Provides a valid SystemState object for testing."""
    return SystemState(
        software_state=SoftwareState(),
        modules=[],
        energy_breakdown=EnergyBreakdown(total=100, complexity=50, coupling=20, constraint=20, debt=10),
        lyapunov_metrics=LyapunovMetrics(phi=1.0, energy=100, test_penalty=0, obligation_penalty=0),
        metadata={"type": "test_state", "mathematical_filters": {"c1": "v1"}}
    )

def test_consult_memory(memory_agent: MemoryAwareAgent, valid_system_state: SystemState):
    """Tests the consult_memory_before_action method."""
    memory_agent.constellation.query_facts.return_value = MagicMock(facts=[])

    guidance = memory_agent.consult_memory_before_action(valid_system_state)

    memory_agent.constellation.query_facts.assert_called_once()
    query_arg = memory_agent.constellation.query_facts.call_args[0][0]

    assert "energy 100" in query_arg.text
    assert query_arg.filters["state_type"] == "test_state"
    assert query_arg.mathematical_filters["c1"] == "v1"

    assert guidance is not None
    assert any("Found 0 relevant patterns" in s for s in guidance.recommendations)

def test_update_memory(memory_agent: MemoryAwareAgent):
    """Tests the update_memory_after_action method."""
    mock_fact = Fact(content={"success": True}, type=FactType.PATTERN)
    mock_encoding = OptimalEncoding(algorithm='none', compressed_data=b'', compression_ratio=1.0, entropy=0.0, bound_verification={}, optimality_proof={}, hash="")
    mock_embedding = np.array([1, 2, 3, 4])
    mock_fact_node = FactNode(id="fact1", fact=mock_fact, encoding=mock_encoding, embedding=mock_embedding, storage_locations={})

    learning_result = MagicMock(pattern_node=mock_fact_node, mathematical_certificate="cert")
    memory_agent.constellation.learn_pattern.return_value = learning_result

    action = AgentAction(agent_id="test", action_type="test_action", params={"p":1})
    result = ActionResult(
        success=True,
        confidence=0.9,
        success_metrics={},
        energy_delta=0,
        convergence_metrics={}
    )

    update = memory_agent.update_memory_after_action(action, result)

    memory_agent.constellation.learn_pattern.assert_called_once()
    assert update is not None
    assert update.learning_certificate == "cert"

def test_apply_physics_principle_workflow(memory_agent: MemoryAwareAgent, valid_system_state: SystemState):
    """Tests the full workflow in apply_physics_principle."""
    memory_agent.constellation.query_facts.return_value = MagicMock(facts=[])

    mock_fact = Fact(content={"success": True}, type=FactType.PATTERN)
    mock_encoding = OptimalEncoding(algorithm='none', compressed_data=b'', compression_ratio=1.0, entropy=0.0, bound_verification={}, optimality_proof={}, hash="")
    mock_embedding = np.array([1, 2, 3, 4])
    mock_fact_node = FactNode(id="fact1", fact=mock_fact, encoding=mock_encoding, embedding=mock_embedding, storage_locations={})
    learning_result = MagicMock(pattern_node=mock_fact_node, mathematical_certificate="cert")
    memory_agent.constellation.learn_pattern.return_value = learning_result

    physics_result = memory_agent.apply_physics_principle(valid_system_state)

    assert memory_agent.constellation.query_facts.call_count == 1
    assert memory_agent.constellation.learn_pattern.call_count == 1
    assert physics_result.status == "SUCCESS"
