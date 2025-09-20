import pytest
from unittest.mock import Mock

from core.orchestrator import Orchestrator

def test_orchestrator_instantiation():
    """
    Tests that the Orchestrator can be instantiated with mock dependencies.
    """
    # Create mock objects for all dependencies
    mock_energy_calculator = Mock()
    mock_lyapunov_monitor = Mock()
    mock_closure_validator = Mock()
    mock_closure_rule_engine = Mock()
    mock_comm_protocol = Mock()

    # Instantiate the Orchestrator
    orchestrator = Orchestrator(
        agents=[Mock()],
        energy_calculator=mock_energy_calculator,
        lyapunov_monitor=mock_lyapunov_monitor,
        closure_validator=mock_closure_validator,
        closure_rule_engine=mock_closure_rule_engine,
        communication_protocol=mock_comm_protocol,
    )

    # Assert that the object was created and is of the correct type
    assert isinstance(orchestrator, Orchestrator)

    # Assert that the dependencies were assigned correctly
    assert orchestrator.energy_calculator is mock_energy_calculator
    assert orchestrator.lyapunov_monitor is mock_lyapunov_monitor
    assert orchestrator.closure_validator is mock_closure_validator
    assert orchestrator.closure_rule_engine is mock_closure_rule_engine
    assert orchestrator.comm_protocol is mock_comm_protocol
