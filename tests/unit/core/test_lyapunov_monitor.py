# tests/unit/core/test_lyapunov_monitor.py

import pytest
from unittest.mock import MagicMock
from core.lyapunov_monitor import LyapunovMonitor
from core.data_models import SystemState, EnergyBreakdown, Obligation, ObligationStatus, LyapunovMetrics, SoftwareState

# Mock SystemState for testing purposes
@pytest.fixture
def mock_state_factory():
    def _create_state(energy_total=100.0, failing_tests=0, open_obligations=0):
        obligations = []
        for i in range(open_obligations):
            ob = MagicMock(spec=Obligation)
            ob.status = ObligationStatus.OPEN
            obligations.append(ob)

        energy_breakdown=EnergyBreakdown(total=energy_total, complexity=energy_total, coupling=0, constraint=0, debt=0)

        # For the purpose of this test, we can create a dummy lyapunov metric.
        # The monitor's `compute` method will calculate the real one.
        lyapunov_metrics = LyapunovMetrics(phi=energy_total, energy=energy_total, test_penalty=0, obligation_penalty=0)

        return SystemState(
            software_state=SoftwareState(),
            energy_breakdown=energy_breakdown,
            lyapunov_metrics=lyapunov_metrics,
            failing_tests=[f"test_{i}" for i in range(failing_tests)],
            obligations=obligations,
        )
    return _create_state

def test_initialization():
    """Test that the LyapunovMonitor initializes correctly."""
    monitor = LyapunovMonitor(kappa=10.0, xi=5.0)
    assert monitor.kappa == 10.0
    assert monitor.xi == 5.0
    assert monitor.history == []

    with pytest.raises(ValueError):
        LyapunovMonitor(kappa=-1.0, xi=5.0)
    with pytest.raises(ValueError):
        LyapunovMonitor(kappa=10.0, xi=-5.0)

def test_compute(mock_state_factory):
    """Test the computation of Lyapunov metrics."""
    monitor = LyapunovMonitor(kappa=10.0, xi=5.0)

    # State with no penalties
    state1 = mock_state_factory(energy_total=100.0, failing_tests=0, open_obligations=0)
    metrics1 = monitor.compute(state1)
    assert metrics1.energy == 100.0
    assert metrics1.test_penalty == 0.0
    assert metrics1.obligation_penalty == 0.0
    assert metrics1.phi == 100.0

    # State with penalties
    state2 = mock_state_factory(energy_total=80.0, failing_tests=2, open_obligations=3)
    metrics2 = monitor.compute(state2)
    assert metrics2.energy == 80.0
    assert metrics2.test_penalty == 10.0 * 2 # kappa * 2
    assert metrics2.obligation_penalty == 5.0 * 3 # xi * 3
    assert metrics2.phi == 80.0 + 20.0 + 15.0 == 115.0

def test_track():
    """Test that tracking adds metrics to the history."""
    monitor = LyapunovMonitor(kappa=1.0, xi=1.0)
    metrics1 = LyapunovMetrics(phi=100, energy=100, test_penalty=0, obligation_penalty=0)
    metrics2 = LyapunovMetrics(phi=90, energy=90, test_penalty=0, obligation_penalty=0)

    monitor.track(metrics1)
    assert monitor.history == [metrics1]

    monitor.track(metrics2)
    assert monitor.history == [metrics1, metrics2]

def test_verify_descent():
    """Test the verification of potential descent."""
    monitor = LyapunovMonitor(kappa=1.0, xi=1.0)

    # Insufficient history
    assert monitor.verify_descent() is True
    monitor.track(LyapunovMetrics(phi=100, energy=100, test_penalty=0, obligation_penalty=0))
    assert monitor.verify_descent() is True

    # Descending potential
    monitor.track(LyapunovMetrics(phi=90, energy=90, test_penalty=0, obligation_penalty=0))
    assert monitor.verify_descent() is True

    # Stable potential
    monitor.track(LyapunovMetrics(phi=90, energy=90, test_penalty=0, obligation_penalty=0))
    assert monitor.verify_descent() is True

    # Ascending potential
    monitor.track(LyapunovMetrics(phi=95, energy=95, test_penalty=0, obligation_penalty=0))
    assert monitor.verify_descent() is False
