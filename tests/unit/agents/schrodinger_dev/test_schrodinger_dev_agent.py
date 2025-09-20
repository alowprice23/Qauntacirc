import pytest
import numpy as np
from unittest.mock import MagicMock, AsyncMock

from agents.schrodinger_dev.agent import SchrodingerDevAgent
from core.types import SystemState, EnergyBreakdown, LyapunovMetrics, SoftwareState, CodeEvolution, CodeState, Hamiltonian, UnitaryOperator, Observable

@pytest.fixture
def mock_llm_client():
    """Provides a mock LLM client."""
    return AsyncMock()

@pytest.fixture
def schrodinger_agent(mock_llm_client):
    """Provides an instance of the SchrodingerDevAgent."""
    return SchrodingerDevAgent(llm_client=mock_llm_client)

@pytest.fixture
def mock_system_state():
    """Provides a mock SystemState configured for the SchrodingerDevAgent."""
    code_state_data = {"state_vector": [1.0, 0.0], "code": "def f(): pass"}
    hamiltonian_data = {"matrix": [[1, 0], [0, -1]]}
    dt = 1.0
    implementations = ["def f(): pass", "def g(): pass"]

    return SystemState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=1.0, complexity=1, coupling=0, constraint=0, debt=0),
        lyapunov_metrics=LyapunovMetrics(phi=1.0, energy=1.0, test_penalty=0, obligation_penalty=0),
        metadata={
            "schrodinger_dev_input": {
                "code_state": code_state_data,
                "hamiltonian": hamiltonian_data,
                "dt": dt,
                "implementations": implementations,
            }
        }
    )

def test_agent_initialization(schrodinger_agent):
    """Tests that the agent initializes correctly."""
    assert schrodinger_agent.physics_principle == "Quantum State Evolution"
    assert schrodinger_agent.code_generator is not None
    assert schrodinger_agent.proof_synthesizer is not None

def test_apply_physics_principle_success(schrodinger_agent, mock_system_state):
    """Tests a successful run of the code evolution process."""
    result = schrodinger_agent.apply_physics_principle(mock_system_state)

    assert isinstance(result, CodeEvolution)
    assert result.success is True
    assert result.agent_name == "SchrodingerDevAgent"
    assert "Code evolution successful" in result.message
    assert result.new_state is not None
    assert isinstance(result.new_state, CodeState)
    assert len(result.new_state.state_vector) == 2
    assert result.energy_change is not None

def test_apply_physics_principle_missing_metadata(schrodinger_agent, mock_system_state):
    """Tests that the agent raises a ValueError if metadata is missing."""
    mock_system_state.metadata = {}  # Remove the required input
    with pytest.raises(ValueError, match="SchrödingerDevAgent requires 'code_state', 'hamiltonian', 'dt', and 'implementations' in metadata."):
        schrodinger_agent.apply_physics_principle(mock_system_state)

def test_measure_observable(schrodinger_agent, mock_system_state):
    """Tests the measurement of the evolution stability."""
    observable = schrodinger_agent.measure_observable(mock_system_state)
    assert isinstance(observable, Observable)
    assert observable.name == "evolution_norm_stability"
    # The value should be close to 0 for a unitary evolution
    assert np.isclose(observable.value, 0.0)

def test_verify_conservation_laws(schrodinger_agent, mock_system_state):
    """Tests the verification of probability conservation."""
    # Create two states with slightly different norms for a failure case
    state_before = mock_system_state.model_copy(deep=True)
    state_after = mock_system_state.model_copy(deep=True)

    state_before.quantum_state = CodeState(state_vector=[1.0, 0.0], code="")
    state_after.quantum_state = CodeState(state_vector=[0.9, 0.1], code="") # Not normalized

    assert schrodinger_agent.verify_conservation_laws(state_before, state_after) == False

    # Test with conserved norm
    state_after.quantum_state.state_vector = [0.0, 1.0]
    assert schrodinger_agent.verify_conservation_laws(state_before, state_after) == True
