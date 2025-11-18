import pytest
from unittest.mock import Mock, call
import numpy as np
import uuid

from agents.base.memory import AgentMemory, Constellation
from core.types import QCState, AgentTask, AgentResult, SoftwareState, EnergyComponents

@pytest.fixture
def mock_state():
    return QCState(
        software_state=SoftwareState(component_versions={}, config_hashes={}),
        energy=100.0,
        energy_components=EnergyComponents(static=50.0, dynamic=30.0, interaction=20.0),
        lyapunov_potential=0.5,
        contraction_factor=0.9,
    )

@pytest.fixture
def mock_proposal():
    return AgentTask(agent_name="test_agent", task_type="test", payload={})

@pytest.fixture
def mock_action():
    return AgentResult(task_id=uuid.uuid4(), agent_name="test_agent", action_taken=True)

def test_constellation_add_and_search():
    constellation = Constellation()
    vec1 = np.array([1.0, 0.0])
    data1 = {"id": 1}
    vec2 = np.array([0.0, 1.0])
    data2 = {"id": 2}

    constellation.add_experience(vec1, data1)
    constellation.add_experience(vec2, data2)

    results = constellation.search(np.array([0.8, 0.2]), k=1)
    assert len(results) == 1
    assert results[0] == data1

def test_agent_memory_featurize_state(mock_state):
    memory = AgentMemory(Constellation())
    vector = memory._featurize_state(mock_state)
    assert isinstance(vector, np.ndarray)
    assert vector.shape == (128,)
    assert np.isclose(np.linalg.norm(vector), 1.0)

def test_agent_memory_record_decision(mock_state, mock_proposal, mock_action):
    constellation_mock = Mock()
    memory = AgentMemory(constellation_mock)

    memory.record_decision(mock_state, mock_proposal, mock_action)

    constellation_mock.add_experience.assert_called_once()
    args, _ = constellation_mock.add_experience.call_args
    assert isinstance(args[0], np.ndarray)
    assert args[1]["state"] == mock_state
    assert args[1]["proposal"] == mock_proposal
    assert args[1]["action"] == mock_action

def test_agent_memory_find_similar_decisions(mock_state):
    constellation_mock = Mock()
    constellation_mock.search.return_value = [{"id": 1}]
    memory = AgentMemory(constellation_mock)

    results = memory.find_similar_decisions(mock_state, top_k=5)

    assert results == [{"id": 1}]
    constellation_mock.search.assert_called_once()
    args, kwargs = constellation_mock.search.call_args
    assert isinstance(args[0], np.ndarray)
    assert kwargs == {"k": 5}

def test_learn_from_outcomes(capsys):
    memory = AgentMemory(Constellation())
    memory.learn_from_outcomes([Mock()], [Mock(), Mock()])
    captured = capsys.readouterr()
    assert "Learning from 1 successes and 2 failures" in captured.out
