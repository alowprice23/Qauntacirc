import pytest
from unittest.mock import Mock, MagicMock

from agents.base.router import AgentRouter

@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.agent_id = "agent_1"
    agent.name = "Test Agent"
    agent.is_active = True
    return agent

@pytest.fixture
def router():
    return AgentRouter()

def test_register_agent(router, mock_agent):
    router.register_agent(mock_agent, ["test_cap"], 1.0)
    assert len(router.agents) == 1
    assert router.agents[0]["id"] == "agent_1"
    assert "test_cap" in router.agents[0]["capabilities"]

def test_enqueue_task(router):
    router.enqueue_task({"name": "task1"}, priority=1)
    router.enqueue_task({"name": "task2"}, priority=0)
    assert len(router.task_queue) == 2
    assert router.task_queue[0][1]["name"] == "task2" # Lowest priority number is first

def test_score_agent_for_task(router, mock_agent):
    router.register_agent(mock_agent, ["cap1", "cap2"], 0.8)
    task = {"required_capabilities": ["cap1"]}
    score = router._score_agent_for_task(router.agents[0], task)
    assert 0 < score < 1

def test_select_agent_for_task(router, mock_agent):
    agent2 = Mock()
    agent2.agent_id = "agent_2"
    agent2.name = "Agent 2"
    agent2.is_active = True

    router.register_agent(mock_agent, ["cap1"], 0.5)
    router.register_agent(agent2, ["cap1", "cap2"], 0.9)

    task = {"required_capabilities": ["cap1", "cap2"]}
    selected_agent = router.select_agent_for_task(task)

    assert selected_agent == agent2

def test_select_inactive_agent(router, mock_agent):
    mock_agent.is_active = False
    router.register_agent(mock_agent, ["cap1"], 1.0)
    task = {"required_capabilities": ["cap1"]}
    selected_agent = router.select_agent_for_task(task)
    assert selected_agent is None

def test_dispatch_task(router, mock_agent):
    router.register_agent(mock_agent, ["cap1"])
    task = {"name": "test_task", "required_capabilities": ["cap1"], "state": Mock()}
    router.enqueue_task(task)

    assert router.dispatch() is True
    mock_agent.run.assert_called_once_with(task["state"])

def test_dispatch_no_suitable_agent(router, mock_agent):
    router.register_agent(mock_agent, ["cap2"])
    task = {"name": "test_task", "required_capabilities": ["cap1"]}
    router.enqueue_task(task)

    assert router.dispatch() is False
    assert len(router.task_queue) == 1 # Task is re-queued

def test_update_agent_score(router, mock_agent):
    router.register_agent(mock_agent, ["cap1"], 0.5)
    router.update_agent_score("agent_1", 0.9)
    assert router.agents[0]["score"] == 0.9
