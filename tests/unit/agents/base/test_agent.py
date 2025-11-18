import pytest
from unittest.mock import Mock, call, patch, MagicMock
import uuid

from agents.base.agent import QuantumAgent
from core.types import QCState as State, AgentTask as Proposal, AgentResult as Action, SoftwareState, EnergyComponents

# A concrete implementation of the abstract QuantumAgent for testing
class ConcreteQuantumAgent(QuantumAgent):
    def analyze_state(self, state: State) -> Proposal:
        return Proposal(agent_name=self.name, task_type="analysis", payload={"analysis": "done"})

    def validate_proposal(self, proposal: Proposal) -> bool:
        return True

    def execute(self, proposal: Proposal) -> Action:
        task_id = proposal.id if hasattr(proposal, 'id') else uuid.uuid4()
        return Action(task_id=task_id, agent_name=self.name, action_taken=True, result={"execution": "done"})

@pytest.fixture
def mock_dependencies():
    metrics_logger = Mock()
    metrics_logger.log_duration.return_value = MagicMock()
    return {
        "name": "test_agent",
        "state_space": Mock(),
        "energy_calculator": Mock(),
        "metrics_logger": metrics_logger,
        "policy_engine": Mock(),
        "agent_memory": Mock(),
        "contracts": [Mock()],
    }

@pytest.fixture
def mock_state():
    # A simplified mock of QCState for testing purposes
    return State(
        software_state=SoftwareState(component_versions={}, config_hashes={}),
        energy=100.0,
        energy_components=EnergyComponents(static=50.0, dynamic=30.0, interaction=20.0),
        lyapunov_potential=0.5,
        contraction_factor=0.9,
    )

def test_agent_initialization(mock_dependencies):
    agent = ConcreteQuantumAgent(**mock_dependencies)
    assert agent.name == "test_agent"
    assert isinstance(agent.agent_id, str)
    assert agent.state_space == mock_dependencies["state_space"]
    assert not agent.is_active

    # Check if metrics are registered
    mock_dependencies["metrics_logger"].register_counter.assert_any_call(
        "agent_test_agent_proposals", "Number of proposals generated"
    )
    mock_dependencies["metrics_logger"].register_counter.assert_any_call(
        "agent_test_agent_executions", "Number of successful executions"
    )
    mock_dependencies["metrics_logger"].register_histogram.assert_called_with(
        "agent_test_agent_execution_duration", "Duration of agent execution"
    )

def test_agent_activation_deactivation(mock_dependencies):
    agent = ConcreteQuantumAgent(**mock_dependencies)
    assert not agent.is_active
    agent.activate()
    assert agent.is_active
    agent.deactivate()
    assert not agent.is_active

def test_run_successful_execution(mock_dependencies, mock_state):
    agent = ConcreteQuantumAgent(**mock_dependencies)
    agent.activate()

    mock_dependencies["contracts"][0].check_preconditions.return_value = True
    mock_dependencies["contracts"][0].check_postconditions.return_value = True
    mock_dependencies["policy_engine"].validate.return_value = True

    action = agent.run(mock_state)

    assert action is not None
    assert action.action_taken is True

    mock_dependencies["contracts"][0].check_preconditions.assert_called_once_with(mock_state)
    mock_dependencies["policy_engine"].validate.assert_called_once()
    mock_dependencies["contracts"][0].check_postconditions.assert_called_once()
    mock_dependencies["metrics_logger"].increment_counter.assert_has_calls([
        call("agent_test_agent_proposals"),
        call("agent_test_agent_executions")
    ])
    mock_dependencies["agent_memory"].record_decision.assert_called_once()

def test_run_inactive_agent(mock_dependencies, mock_state):
    agent = ConcreteQuantumAgent(**mock_dependencies)
    action = agent.run(mock_state)
    assert action is None
    mock_dependencies["metrics_logger"].increment_counter.assert_not_called()

def test_run_failed_precondition(mock_dependencies, mock_state):
    mock_dependencies["contracts"][0].check_preconditions.side_effect = ValueError("Precondition failed")
    agent = ConcreteQuantumAgent(**mock_dependencies)
    agent.activate()

    action = agent.run(mock_state)

    assert action is None
    mock_dependencies["metrics_logger"].increment_counter.assert_called_with("agent_test_agent_errors")

def test_run_failed_proposal_validation(mock_dependencies, mock_state):
    agent = ConcreteQuantumAgent(**mock_dependencies)
    agent.activate()

    with patch.object(agent, 'validate_proposal', return_value=False):
        action = agent.run(mock_state)
        assert action is None
        # No error counter for a simple validation fail
        error_call = call("agent_test_agent_errors")
        assert error_call not in mock_dependencies["metrics_logger"].increment_counter.call_args_list

def test_run_failed_policy_validation(mock_dependencies, mock_state):
    mock_dependencies["policy_engine"].validate.return_value = False
    agent = ConcreteQuantumAgent(**mock_dependencies)
    agent.activate()

    action = agent.run(mock_state)

    assert action is None
    error_call = call("agent_test_agent_errors")
    assert error_call not in mock_dependencies["metrics_logger"].increment_counter.call_args_list

def test_run_failed_postcondition(mock_dependencies, mock_state):
    mock_dependencies["contracts"][0].check_postconditions.side_effect = ValueError("Postcondition failed")
    agent = ConcreteQuantumAgent(**mock_dependencies)
    agent.activate()

    action = agent.run(mock_state)

    assert action is None
    mock_dependencies["metrics_logger"].increment_counter.assert_called_with("agent_test_agent_errors")

def test_run_execution_exception(mock_dependencies, mock_state):
    agent = ConcreteQuantumAgent(**mock_dependencies)
    agent.activate()

    with patch.object(agent, 'execute', side_effect=Exception("Execution failed")):
        action = agent.run(mock_state)
        assert action is None
        mock_dependencies["metrics_logger"].increment_counter.assert_called_with("agent_test_agent_errors")
