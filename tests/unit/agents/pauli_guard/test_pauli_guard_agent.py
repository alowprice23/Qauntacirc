import pytest
import numpy as np
from agents.pauli_guard.agent import PauliGuardAgent
from core.types import (
    SystemState, ModuleState, OrthogonalizationResult, EnergyBreakdown,
    LyapunovMetrics, SoftwareState
)

@pytest.fixture
def pauli_agent():
    """Fixture for a PauliGuardAgent instance."""
    return PauliGuardAgent()

@pytest.fixture
def system_state_with_overlapping_modules():
    """Fixture for a SystemState with non-orthogonal modules."""
    module_data = [
        {"id": "module_a", "state_vector": [1.0, 0.5, 0.1], "code": "..."},
        {"id": "module_b", "state_vector": [0.8, 0.6, 0.2], "code": "..."}, # Overlaps with a
        {"id": "module_c", "state_vector": [-0.5, 1.0, 0.3], "code": "..."}  # Mostly orthogonal to a
    ]

    state = SystemState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0),
        metadata={
            "pauli_guard_input": {
                "modules": module_data
            }
        }
    )
    return state

def test_apply_physics_principle_identifies_violations(pauli_agent, system_state_with_overlapping_modules):
    """
    Tests that apply_physics_principle correctly identifies orthogonality violations
    and proposes a valid orthogonalization result.
    """
    # Act
    result = pauli_agent.apply_physics_principle(system_state_with_overlapping_modules)

    # Assert
    assert isinstance(result, OrthogonalizationResult)
    assert result.success is True
    assert result.agent_name == "pauli_guard"
    assert result.physics_principle == "Exclusion Principle"

    # Check that violations were found
    assert len(result.violations) > 0
    assert result.eliminated_duplicates > 0

    # Check that a shared component was identified for the violation
    assert len(result.shared_components) == len(result.violations)
    assert "module_a" in result.shared_components[0].used_by
    assert "module_b" in result.shared_components[0].used_by

    # Check that orthogonalization improved the state
    assert result.orthogonality_improvement > 0
    assert len(result.modules) == len(system_state_with_overlapping_modules.metadata["pauli_guard_input"]["modules"])

def test_apply_physics_principle_no_modules(pauli_agent):
    """
    Tests that the agent handles a system state with no modules to analyze.
    """
    state = SystemState(
        software_state=SoftwareState(),
        energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=20.0, debt=0.0),
        lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0),
        metadata={"pauli_guard_input": {"modules": []}}
    )

    # Act
    result = pauli_agent.apply_physics_principle(state)

    # Assert
    assert isinstance(result, OrthogonalizationResult)
    assert result.success is True
    assert result.eliminated_duplicates == 0
    assert result.orthogonality_improvement == 0.0
    assert len(result.violations) == 0
