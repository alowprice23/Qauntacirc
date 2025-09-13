# tests/unit/core/test_convergence_engine.py

import pytest
from unittest.mock import MagicMock
import numpy as np
from typing import Optional

from core.convergence_engine import ConvergenceEngine, ConvergenceCriteria
from core.data_models import QCState, LyapunovResult, SoftwareState, EnergyComponents, EnergyBreakdown, LyapunovMetrics, QuantumState
from core.lyapunov_monitor import LyapunovMonitor
from core.lyapunov_function import LyapunovFunction
from core.two_phase_annealer import TwoPhaseAnnealer

# Mock QCState for testing purposes
class MockQCState(QCState):
    def __init__(self, energy, potential, failing_tests=0, open_obligations=0):
        super().__init__(
            software_state=SoftwareState(),
            energy_breakdown=EnergyBreakdown(total=energy, complexity=energy, coupling=0, constraint=0, debt=0),
            lyapunov_metrics=LyapunovMetrics(phi=potential, energy=energy, test_penalty=failing_tests, obligation_penalty=open_obligations),
            contraction_factor=0.5,
            failing_tests=[str(i) for i in range(failing_tests)],
            obligations=[MagicMock() for _ in range(open_obligations)],
        )

MockQCState.model_rebuild()

@pytest.fixture
def lyapunov_function():
    """Fixture for a LyapunovFunction instance."""
    return LyapunovFunction(kappa=1.0, xi=1.0)

@pytest.fixture
def lyapunov_monitor():
    """Fixture for a LyapunovMonitor instance."""
    return LyapunovMonitor(kappa=1.0, xi=1.0)

@pytest.fixture
def mock_annealer():
    """Fixture for a mocked TwoPhaseAnnealer."""
    annealer = MagicMock(spec=TwoPhaseAnnealer)
    annealer.is_finished = False
    annealer.phase = "B" # Assume exploitation phase
    annealer.check_convergence = MagicMock(return_value=True)
    return annealer

@pytest.fixture
def stable_state_history():
    """Fixture for a history of states that should be considered stable."""
    return [MockQCState(energy=1.0, potential=1.0) for _ in range(100)]

def test_initialization():
    """Test that the ConvergenceEngine initializes correctly."""
    criteria = ConvergenceCriteria(energy_variance_threshold=1e-5)
    engine = ConvergenceEngine(criteria)
    assert engine.criteria.energy_variance_threshold == 1e-5

def test_insufficient_history(lyapunov_monitor):
    """Test that convergence is False if history is too short."""
    engine = ConvergenceEngine()
    history = [MockQCState(1.0, 1.0) for _ in range(10)] # Default window is 50
    result = engine.check_convergence(history, lyapunov_monitor, MagicMock())
    assert not result["converged"]
    assert result["reason"] == "Insufficient history"

def test_annealer_finished(lyapunov_monitor):
    """Test that convergence is True if the annealer is finished."""
    engine = ConvergenceEngine()
    mock_annealer_finished = MagicMock(spec=TwoPhaseAnnealer)
    mock_annealer_finished.is_finished = True
    history = [MockQCState(1.0, 1.0) for _ in range(100)]
    result = engine.check_convergence(history, lyapunov_monitor, mock_annealer_finished)
    assert result["converged"]
    assert result["reason"] == "Annealer finished temperature schedule."

def test_energy_stability_check():
    """Test the energy stability check logic."""
    engine = ConvergenceEngine(ConvergenceCriteria(energy_variance_threshold=0.01))

    # Stable energy
    stable_history = [MockQCState(energy=1.0 + np.random.randn() * 0.05, potential=1.0) for _ in range(100)]
    is_stable, variance = engine._check_energy_stability(stable_history)
    assert is_stable
    assert variance < 0.01

    # Unstable energy
    unstable_history = [MockQCState(energy=1.0 + np.random.randn() * 0.5, potential=1.0) for _ in range(100)]
    is_stable, variance = engine._check_energy_stability(unstable_history)
    assert not is_stable
    assert variance > 0.01

def test_lyapunov_stability_check(lyapunov_monitor):
    """Test the Lyapunov stability check logic."""
    engine = ConvergenceEngine(ConvergenceCriteria(lyapunov_exponent_threshold=-1e-3))

    # Stable case
    stable_history = [MockQCState(energy=1.0 * (0.9**i), potential=1.0 * (0.9**i)) for i in range(20)]
    for state in stable_history:
        lyapunov_monitor.track(lyapunov_monitor.compute(state))
    is_stable, exponent = engine._check_lyapunov_stability(lyapunov_monitor)
    assert is_stable
    assert exponent < -1e-3

    # Unstable case
    unstable_monitor = LyapunovMonitor(kappa=1.0, xi=1.0)
    unstable_history = [MockQCState(energy=1.0 * (1.1**i), potential=1.0 * (1.1**i)) for i in range(20)]
    for state in unstable_history:
        unstable_monitor.track(unstable_monitor.compute(state))
    is_stable, exponent = engine._check_lyapunov_stability(unstable_monitor)
    assert not is_stable
    assert exponent > -1e-3

def test_potential_drift_check():
    """Test the potential drift check logic."""
    engine = ConvergenceEngine(ConvergenceCriteria(potential_drift_threshold=1e-4))

    # Stable potential (low drift)
    stable_history = [MockQCState(energy=1.0, potential=1.0 - i * 1e-5) for i in range(100)]
    is_stable, drift = engine._check_potential_drift(stable_history)
    assert is_stable
    assert abs(drift) < 1e-4

    # Unstable potential (high drift)
    unstable_history = [MockQCState(energy=1.0, potential=1.0 - i * 1e-2) for i in range(100)]
    is_stable, drift = engine._check_potential_drift(unstable_history)
    assert not is_stable
    assert abs(drift) > 1e-4

def test_full_convergence_all_criteria_met(lyapunov_monitor, mock_annealer):
    """Test for overall convergence when all criteria are met."""
    criteria = ConvergenceCriteria(lyapunov_exponent_threshold=-0.0, potential_drift_threshold=1e-5, energy_variance_threshold=1e-9)
    engine = ConvergenceEngine(criteria=criteria)
    stable_history = [MockQCState(energy=1.0 - i * 1e-9, potential=0, failing_tests=0, open_obligations=0) for i in range(100)]
    for state in stable_history:
        lyapunov_monitor.track(lyapunov_monitor.compute(state))
    result = engine.check_convergence(stable_history, lyapunov_monitor, mock_annealer)

    assert result["converged"]
    assert result["reason"] == "Converged based on multiple stability criteria."
    assert result["checks"]["energy_stability"]["succeeded"]
    assert result["checks"]["lyapunov_stability"]["succeeded"]
    assert result["checks"]["potential_stability"]["succeeded"]
    assert result["checks"]["contractive_mapping"]["succeeded"]
    assert result["checks"]["in_exploitation_phase"]

def test_full_convergence_one_criterion_fails(lyapunov_monitor, mock_annealer):
    """Test that convergence is False if one of the criteria fails."""
    engine = ConvergenceEngine()

    # Make energy unstable
    unstable_energy_history = [MockQCState(energy=np.random.randn(), potential=1.0) for _ in range(100)]
    for state in unstable_energy_history:
        lyapunov_monitor.track(lyapunov_monitor.compute(state))
    result = engine.check_convergence(unstable_energy_history, lyapunov_monitor, mock_annealer)
    assert not result["converged"]
    assert not result["checks"]["energy_stability"]["succeeded"]

    # Make Lyapunov unstable
    unstable_lyapunov_monitor = LyapunovMonitor(kappa=1.0, xi=1.0)
    unstable_history = [MockQCState(energy=1.0 * (1.1**i), potential=1.0 * (1.1**i)) for i in range(100)]
    for state in unstable_history:
        unstable_lyapunov_monitor.track(unstable_lyapunov_monitor.compute(state))
    result = engine.check_convergence(unstable_history, unstable_lyapunov_monitor, mock_annealer)
    assert not result["converged"]
    assert not result["checks"]["lyapunov_stability"]["succeeded"]

    # Not in exploitation phase
    mock_annealer.phase = "A" # Exploration
    stable_lyapunov_monitor = LyapunovMonitor(kappa=1.0, xi=1.0)
    stable_history = [MockQCState(energy=1.0 * (0.9**i), potential=1.0 * (0.9**i)) for i in range(100)]
    for state in stable_history:
        stable_lyapunov_monitor.track(stable_lyapunov_monitor.compute(state))
    result = engine.check_convergence(stable_history, stable_lyapunov_monitor, mock_annealer)
    assert not result["converged"]
    assert not result["checks"]["in_exploitation_phase"]
