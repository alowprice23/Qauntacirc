import pytest
from unittest.mock import Mock
from core.types import CompletenessProof
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

from unittest.mock import patch

def test_irrefutability_gate_integration():
    """
    Tests that the irrefutability gate is called during the gate running process.
    """
    # Mock dependencies
    mock_energy_calculator = Mock()
    mock_lyapunov_monitor = Mock()
    mock_closure_validator = Mock()
    mock_closure_rule_engine = Mock()
    mock_comm_protocol = Mock()

    # Mock IrrefutabilityEngine
    mock_irrefutability_engine = Mock()
    mock_irrefutability_result = Mock()
    mock_irrefutability_result.decision_irrefutable = True
    mock_irrefutability_engine.verify_acceptance_irrefutability.return_value = mock_irrefutability_result

    with patch('core.orchestrator.IrrefutabilityEngine', return_value=mock_irrefutability_engine):
        # Instantiate the Orchestrator
        orchestrator = Orchestrator(
            agents=[Mock()],
            energy_calculator=mock_energy_calculator,
            lyapunov_monitor=mock_lyapunov_monitor,
            closure_validator=mock_closure_validator,
            closure_rule_engine=mock_closure_rule_engine,
            communication_protocol=mock_comm_protocol,
        )

        # Mock SystemState and other gate results
        mock_state = Mock()
        mock_state.modules = []
        mock_state.requirements = []
        mock_state.obligations = []
        mock_state.metadata = {}

        mock_closure_result = Mock()
        mock_closure_result.is_closed = True
        mock_closure_result.is_minimal = True
        mock_closure_result.completeness_proof = CompletenessProof(
            obligation_count=0,
            proof_steps=[],
            verification_method="mock",
            confidence=1.0
        )
        orchestrator.closure_rule_engine.verify_closure.return_value = mock_closure_result

        # Run gates
        orchestrator.run_gates(mock_state)

        # Assert that the irrefutability engine was called
        mock_irrefutability_engine.verify_acceptance_irrefutability.assert_called_once()
