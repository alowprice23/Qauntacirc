import pytest
from unittest.mock import Mock, call
import numpy as np
import uuid

from agents.base.contracts import (
    Contract,
    EnergyCondition,
    LyapunovCondition,
    ClosureRuleCondition,
)
from core.types import QCState, AgentResult, SoftwareState, EnergyComponents, QuantumState, LyapunovMetrics, EnergyBreakdown, QuantumState

@pytest.fixture
def mock_state():
    return QCState(
        software_state=SoftwareState(),
        quantum_state=QuantumState(state_vector=[complex(1.0), complex(0.0)]),
        energy_breakdown=EnergyBreakdown(
            total=100.0,
            complexity=50.0,
            coupling=30.0,
            constraint=20.0,
            debt=0.0,
        ),
        lyapunov_metrics=LyapunovMetrics(
            phi=0.5,
            energy=100.0,
            test_penalty=0.0,
            obligation_penalty=0.0,
        ),
        contraction_factor=0.9,
    )

@pytest.fixture
def mock_action():
    return AgentResult(
        task_id=uuid.uuid4(),
        agent_name="test_agent",
        action_taken=True,
        result={"delta_vector": [0.1, -0.1]}
    )

def test_contract_check_preconditions(mock_state):
    precondition1 = Mock()
    precondition1.check.return_value = True
    precondition2 = Mock()
    precondition2.check.return_value = True

    contract = Contract("test_contract", [precondition1, precondition2], [])

    assert contract.check_preconditions(mock_state) is True
    precondition1.check.assert_called_once_with(state=mock_state)
    precondition2.check.assert_called_once_with(state=mock_state)

def test_contract_check_preconditions_fail(mock_state):
    precondition1 = Mock()
    precondition1.check.return_value = True
    precondition2 = Mock()
    precondition2.check.return_value = False

    contract = Contract("test_contract", [precondition1, precondition2], [])

    assert contract.check_preconditions(mock_state) is False

def test_contract_check_postconditions(mock_state, mock_action):
    postcondition1 = Mock()
    postcondition1.check.return_value = True
    postcondition2 = Mock()
    postcondition2.check.return_value = True

    contract = Contract("test_contract", [], [postcondition1, postcondition2])

    assert contract.check_postconditions(mock_state, mock_action) is True
    postcondition1.check.assert_called_once_with(state=mock_state, action=mock_action)
    postcondition2.check.assert_called_once_with(state=mock_state, action=mock_action)

def test_contract_check_postconditions_fail(mock_state, mock_action):
    postcondition1 = Mock()
    postcondition1.check.return_value = True
    postcondition2 = Mock()
    postcondition2.check.return_value = False

    contract = Contract("test_contract", [], [postcondition1, postcondition2])

    assert contract.check_postconditions(mock_state, mock_action) is False

def test_energy_condition(mock_state):
    solver = Mock()
    solver.solve.return_value = True
    condition = EnergyCondition(solver, max_energy=150.0)

    assert condition.check(state=mock_state) is True
    solver.solve.assert_called_once_with(["energy <= 150.0"], {"energy": 100.0})

def test_energy_condition_fail(mock_state):
    solver = Mock()
    solver.solve.return_value = False
    condition = EnergyCondition(solver, max_energy=50.0)

    assert condition.check(state=mock_state) is False
    solver.solve.assert_called_once_with(["energy <= 50.0"], {"energy": 100.0})

def test_lyapunov_condition(mock_state, mock_action):
    stability_func = Mock(return_value=True)
    condition = LyapunovCondition(stability_func=stability_func)

    assert condition.check(state=mock_state, action=mock_action) is True
    # The stability_func is called with a list, not a numpy array.
    stability_func.assert_called_once_with([1.1, -0.1])

def test_lyapunov_condition_fail(mock_state, mock_action):
    stability_func = Mock(return_value=False)
    condition = LyapunovCondition(stability_func=stability_func)

    assert condition.check(state=mock_state, action=mock_action) is False

def test_closure_rule_condition(mock_state, mock_action):
    rule = Mock()
    rule.is_satisfied.return_value = True
    condition = ClosureRuleCondition(rule)

    assert condition.check(state=mock_state, action=mock_action) is True
    rule.is_satisfied.assert_called_once_with(mock_state, mock_action)

def test_closure_rule_condition_fail(mock_state, mock_action):
    rule = Mock()
    rule.is_satisfied.return_value = False
    condition = ClosureRuleCondition(rule)

    assert condition.check(state=mock_state, action=mock_action) is False
