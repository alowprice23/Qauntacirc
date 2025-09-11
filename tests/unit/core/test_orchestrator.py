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
    mock_annealer = Mock()
    mock_functor = Mock()
    mock_closure_rules = Mock()

    # Instantiate the Orchestrator
    orchestrator = Orchestrator(
        agents=[Mock()],
        energy_calculator=mock_energy_calculator,
        lyapunov_monitor=mock_lyapunov_monitor,
        annealer=mock_annealer,
        functor=mock_functor,
        closure_rules=mock_closure_rules,
    )

    # Assert that the object was created and is of the correct type
    assert isinstance(orchestrator, Orchestrator)

    # Assert that the dependencies were assigned correctly
    assert orchestrator.energy_calculator is mock_energy_calculator
    assert orchestrator.lyapunov_monitor is mock_lyapunov_monitor
    assert orchestrator.annealer is mock_annealer
    assert orchestrator.functor is mock_functor
    assert orchestrator.closure_rules is mock_closure_rules
