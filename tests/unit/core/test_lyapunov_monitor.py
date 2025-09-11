# tests/unit/core/test_lyapunov_monitor.py

import pytest
import numpy as np
from core.lyapunov_monitor import LyapunovMonitor
from core.types import QCState, LyapunovResult

# Mock QCState, we only need the lyapunov_potential for most tests
class MockQCState:
    def __init__(self, potential):
        self.lyapunov_potential = potential
        # Add other attributes to satisfy the type hint if necessary
        self.energy = 0
        self.energy_components = None

def test_initialization():
    monitor = LyapunovMonitor(excursion_bound=2.0, convergence_threshold=1e-5)
    assert monitor.excursion_bound == 2.0
    assert monitor.convergence_threshold == 1e-5
    assert monitor.potential_history == []
    assert monitor.min_potential is None

def test_reset():
    monitor = LyapunovMonitor()
    monitor.track_state(MockQCState(10.0))
    monitor.track_state(MockQCState(5.0))
    monitor.reset()
    assert monitor.potential_history == []
    assert monitor.state_history == []
    assert monitor.min_potential is None

def test_track_state():
    monitor = LyapunovMonitor()
    state1 = MockQCState(10.0)
    state2 = MockQCState(5.0)

    monitor.track_state(state1)
    assert monitor.potential_history == [10.0]
    assert monitor.state_history == [state1]
    assert monitor.min_potential == 10.0

    monitor.track_state(state2)
    assert monitor.potential_history == [10.0, 5.0]
    assert monitor.state_history == [state1, state2]
    assert monitor.min_potential == 5.0

def test_track_excursion():
    monitor = LyapunovMonitor(excursion_bound=1.5)
    monitor.track_state(MockQCState(10.0))
    monitor.track_state(MockQCState(8.0))

    # No excursion
    is_excursion, ratio = monitor.track_excursion()
    assert not is_excursion
    assert ratio == 8.0 / 8.0 # Min potential is now 8

    monitor.track_state(MockQCState(12.1)) # 12.1 / 8 = 1.5125 > 1.5
    is_excursion, ratio = monitor.track_excursion()
    assert is_excursion
    assert ratio == pytest.approx(12.1 / 8.0)

def test_verify_stability_insufficient_data():
    monitor = LyapunovMonitor()
    monitor.track_state(MockQCState(10.0))
    result = monitor.verify_stability()
    assert result.convergence_status == "insufficient_data"
    assert result.exponent == 0.0

def test_verify_stability_stable_system():
    monitor = LyapunovMonitor(convergence_threshold=1e-3)
    # Exponentially decreasing potential -> stable
    potentials = [10.0 * (0.9**i) for i in range(20)]
    for p in potentials:
        monitor.track_state(MockQCState(p))

    result = monitor.verify_stability()
    assert result.convergence_status == "stable"
    assert result.exponent < -monitor.convergence_threshold

def test_verify_stability_unstable_system():
    monitor = LyapunovMonitor(convergence_threshold=1e-3)
    # Exponentially increasing potential -> unstable
    potentials = [1.0 * (1.1**i) for i in range(20)]
    for p in potentials:
        monitor.track_state(MockQCState(p))

    result = monitor.verify_stability()
    assert result.convergence_status == "unstable"
    assert result.exponent > monitor.convergence_threshold

def test_verify_stability_marginal_system():
    monitor = LyapunovMonitor(convergence_threshold=1e-3)
    # Sinusoidal potential -> marginal (on average)
    potentials = [10 + np.sin(i / 5.0) for i in range(50)]
    for p in potentials:
        monitor.track_state(MockQCState(p))

    result = monitor.verify_stability()
    assert result.convergence_status == "marginal"
    assert abs(result.exponent) <= monitor.convergence_threshold

def test_predict_convergence_stable():
    monitor = LyapunovMonitor()
    potentials = [10.0, 8.0, 6.4, 5.12] # Converging
    for p in potentials:
        monitor.track_state(MockQCState(p))

    # Mock the stability result to be predictable
    monitor.verify_stability = lambda: LyapunovResult(is_stable=True, exponent=-0.2, convergence_status="stable", iterations=4)

    time_to_converge = monitor.predict_convergence(target_potential=1.0)
    assert time_to_converge is not None
    # log(1.0 / 5.12) / -0.2 = -1.63 / -0.2 = 8.15
    assert time_to_converge == pytest.approx(np.log(1.0 / 5.12) / -0.2)

def test_predict_convergence_unstable():
    monitor = LyapunovMonitor()
    potentials = [10.0, 12.0, 14.4] # Diverging
    for p in potentials:
        monitor.track_state(MockQCState(p))

    time_to_converge = monitor.predict_convergence(target_potential=1.0)
    assert time_to_converge is None

def test_verify_martingale_property_supermartingale():
    monitor = LyapunovMonitor()
    # A decreasing sequence is a supermartingale
    potentials = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    for p in potentials:
        monitor.track_state(MockQCState(p))

    is_super, drift = monitor.verify_martingale_property()
    assert is_super
    assert drift < 0

def test_verify_martingale_property_not_supermartingale():
    monitor = LyapunovMonitor()
    # An increasing sequence is not a supermartingale
    potentials = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for p in potentials:
        monitor.track_state(MockQCState(p))

    is_super, drift = monitor.verify_martingale_property()
    assert not is_super
    assert drift > 0
