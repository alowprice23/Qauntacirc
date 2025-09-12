import pytest
from unittest.mock import Mock, call
import uuid

from agents.base.metrics import AgentMetrics
from core.types import AgentResult, QCState, SoftwareState, EnergyBreakdown, LyapunovMetrics

@pytest.fixture
def mock_logger():
    return Mock()

@pytest.fixture
def mock_energy_calculator():
    return Mock()

@pytest.fixture
def agent_metrics(mock_logger, mock_energy_calculator):
    return AgentMetrics("test_agent", mock_logger, mock_energy_calculator)

def test_initialization(agent_metrics, mock_logger):
    prefix = "agent_test_agent"
    expected_calls = [
        call(f"{prefix}_proposals", "Number of proposals generated"),
        call(f"{prefix}_executions", "Number of successful executions"),
        call(f"{prefix}_errors", "Number of errors encountered"),
    ]
    mock_logger.register_counter.assert_has_calls(expected_calls, any_order=True)

    expected_hist_calls = [
        call(f"{prefix}_execution_duration_seconds", "Execution duration in seconds"),
        call(f"{prefix}_energy_impact", "Energy impact of executed actions"),
    ]
    mock_logger.register_histogram.assert_has_calls(expected_hist_calls, any_order=True)

def test_track_proposal(agent_metrics, mock_logger):
    agent_metrics.track_proposal()
    mock_logger.increment_counter.assert_called_once_with("agent_test_agent_proposals")

def test_track_error(agent_metrics, mock_logger):
    agent_metrics.track_error()
    mock_logger.increment_counter.assert_called_once_with("agent_test_agent_errors")

def test_track_execution(agent_metrics, mock_logger, mock_energy_calculator):
    duration = 1.23
    action = AgentResult(task_id=uuid.uuid4(), agent_name="test_agent", action_taken=True)
    energy_breakdown = EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0)
    lyapunov_metrics = LyapunovMetrics(phi=100.5, energy=100.0, test_penalty=0.5, obligation_penalty=0.0)
    state = QCState(
        software_state=SoftwareState(component_versions={}, config_hashes={}),
        energy_breakdown=energy_breakdown,
        lyapunov_metrics=lyapunov_metrics,
        contraction_factor=0.9,
    )
    mock_energy_calculator.calculate_action_energy.return_value = -10.5

    agent_metrics.track_execution(duration, action, state)

    mock_logger.increment_counter.assert_called_once_with("agent_test_agent_executions")
    mock_logger.observe_histogram.assert_has_calls([
        call("agent_test_agent_execution_duration_seconds", duration),
        call("agent_test_agent_energy_impact", -10.5),
    ])
    mock_energy_calculator.calculate_action_energy.assert_called_once_with(action)

def test_get_success_rate(agent_metrics, mock_logger):
    prefix = "agent_test_agent"
    mock_logger.get_counter_value.side_effect = lambda name: {
        f"{prefix}_proposals": 10,
        f"{prefix}_executions": 8,
    }[name]

    assert agent_metrics.get_success_rate() == 0.8

def test_get_success_rate_no_proposals(agent_metrics, mock_logger):
    prefix = "agent_test_agent"
    mock_logger.get_counter_value.side_effect = lambda name: {
        f"{prefix}_proposals": 0,
        f"{prefix}_executions": 0,
    }[name]

    assert agent_metrics.get_success_rate() == 1.0
