import pytest
from unittest.mock import Mock

from agents.base.policies import (
    PolicyEngine,
    RigorPolicy,
    EnergyBudgetPolicy,
)
from core.types import AgentTask

@pytest.fixture
def mock_proposal():
    return AgentTask(
        agent_name="test_agent",
        task_type="test",
        payload={"metadata": {}}
    )

def test_policy_engine(mock_proposal):
    policy1 = Mock()
    policy1.check.return_value = True
    policy2 = Mock()
    policy2.check.return_value = True

    engine = PolicyEngine([policy1, policy2])

    assert engine.validate(mock_proposal) is True
    policy1.check.assert_called_once_with(mock_proposal)
    policy2.check.assert_called_once_with(mock_proposal)

def test_policy_engine_fail(mock_proposal):
    policy1 = Mock()
    policy1.check.return_value = True
    policy2 = Mock()
    policy2.check.return_value = False

    engine = PolicyEngine([policy1, policy2])

    assert engine.validate(mock_proposal) is False

def test_rigor_policy(mock_proposal):
    policy = RigorPolicy(required_rigor=0.8)
    mock_proposal.payload["metadata"]["rigor"] = 0.9
    assert policy.check(mock_proposal) is True

def test_rigor_policy_fail(mock_proposal):
    policy = RigorPolicy(required_rigor=0.8)
    mock_proposal.payload["metadata"]["rigor"] = 0.7
    assert policy.check(mock_proposal) is False

def test_rigor_policy_no_rigor(mock_proposal):
    policy = RigorPolicy(required_rigor=0.8)
    assert policy.check(mock_proposal) is False

def test_energy_budget_policy(mock_proposal):
    error_budget = Mock()
    error_budget.is_sufficient.return_value = True
    policy = EnergyBudgetPolicy(error_budget)

    mock_proposal.payload["metadata"]["estimated_energy_cost"] = 50.0

    assert policy.check(mock_proposal) is True
    error_budget.is_sufficient.assert_called_once_with(50.0)

def test_energy_budget_policy_fail(mock_proposal):
    error_budget = Mock()
    error_budget.is_sufficient.return_value = False
    policy = EnergyBudgetPolicy(error_budget)

    mock_proposal.payload["metadata"]["estimated_energy_cost"] = 150.0

    assert policy.check(mock_proposal) is False
    error_budget.is_sufficient.assert_called_once_with(150.0)
