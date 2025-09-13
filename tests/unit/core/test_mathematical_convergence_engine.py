import pytest
import numpy as np
import asyncio

from core.data_models import SystemState
from core.mathematical_convergence_engine import TwoPhaseConvergenceEngine

# --- Test Fixtures and Helper Functions ---

def quadratic_energy(position: np.ndarray) -> float:
    """A simple convex energy function with a minimum at (0,0)."""
    return np.sum(position**2)

def quadratic_gradient(position: np.ndarray) -> np.ndarray:
    """The gradient of the quadratic energy function."""
    return 2 * position

@pytest.fixture
def initial_state_simple():
    """Provides a starting state for the simple quadratic problem."""
    position = np.array([10.0, -15.0])
    return SystemState(
        energy=quadratic_energy(position),
        position=position
    )

@pytest.fixture
def convergence_engine_simple():
    """Provides a pre-configured engine for the simple quadratic problem."""
    return TwoPhaseConvergenceEngine(
        energy_fn=quadratic_energy,
        gradient_fn=quadratic_gradient,
        optimum_position=np.array([0.0, 0.0])
    )

# --- Test Cases ---

@pytest.mark.asyncio
async def test_engine_converges_on_simple_problem(convergence_engine_simple, initial_state_simple):
    """
    Tests if the engine can successfully converge on a simple, convex problem.
    """
    # Arrange
    engine = convergence_engine_simple

    # Act
    result = await engine.execute_two_phase_optimization(
        initial_state=initial_state_simple,
        target_tolerance=1e-7
    )

    # Assert
    assert result.success is True, "The engine should report successful convergence."
    assert result.error is None, "There should be no errors during convergence."

    # Check final state
    final_position = result.final_state.position
    final_energy = result.final_state.energy
    assert np.linalg.norm(final_position) < 1e-3, "The final position should be very close to the optimum (0,0)."
    assert final_energy < 1e-6, "The final energy should be very close to 0."

    # Check mathematical guarantees
    assert result.contraction_factor is not None
    assert result.contraction_factor < 1.0, "The measured contraction factor (lambda) must be less than 1."

    assert result.convergence_proof is not None
    assert result.convergence_proof.is_verified is True, "The convergence proof should be marked as verified."

    assert result.mathematical_certificate is not None
    assert "guaranteed by Banach" in result.mathematical_certificate.summary, "The certificate should confirm the guarantee."
    assert result.mathematical_certificate.conditions_verified["is_contraction_mapping"] is True

@pytest.mark.asyncio
async def test_phase_a_finds_basin(convergence_engine_simple, initial_state_simple):
    """
    Tests that Phase A runs and hands off a reasonable state to Phase B.
    """
    # Arrange
    engine = convergence_engine_simple
    # Make Phase A very short to just test the transition
    engine.phase_a_controller.max_phase_a_iterations = 500
    engine.phase_a_controller.min_phase_a_iterations = 100
    engine.phase_a_controller.c_constant = 0.1 # Cool very fast

    # Act
    # We are only interested in the result of Phase A for this test
    phase_a_result = await engine._execute_phase_a_global_search(initial_state_simple)

    # Assert
    assert phase_a_result is not None
    assert phase_a_result.iterations <= 500
    # The final energy should be lower than the initial energy, but not necessarily zero
    assert phase_a_result.final_state.energy < initial_state_simple.energy
