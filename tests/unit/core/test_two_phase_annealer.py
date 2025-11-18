# tests/unit/core/test_two_phase_annealer.py

import pytest
import numpy as np
from core.two_phase_annealer import TwoPhaseAnnealer
from core.types import QCState

# Mock QCState for testing purposes
class MockQCState:
    def __init__(self, energy):
        self.energy = energy
        # Add other attributes to satisfy the type hint if necessary
        self.lyapunov_potential = 0
        self.energy_components = None

# Default config for tests
@pytest.fixture
def annealer_config():
    return {
        "initial_temp": 100.0,
        "min_temp": 0.1,
        "phase_a_cooling_const": 50.0,
        "phase_b_cooling_rate": 0.95,
        "phase_switch_window": 10,
        "convergence_window": 10,
        "convergence_tolerance": 1e-4,
    }

@pytest.fixture
def annealer(annealer_config):
    return TwoPhaseAnnealer(annealer_config)

def test_initialization(annealer, annealer_config):
    assert annealer.initial_temp == annealer_config["initial_temp"]
    assert annealer.min_temp == annealer_config["min_temp"]
    assert annealer.phase == "A"
    assert annealer.temperature == annealer.initial_temp

def test_initialize_state(annealer):
    initial_state = MockQCState(energy=500)
    annealer.initialize_state(initial_state)
    assert annealer.current_state == initial_state
    assert annealer.energy_history == [500]
    assert annealer.temperature == annealer.initial_temp # Resets temperature
    assert annealer.phase == "A" # Resets phase

def test_should_accept(annealer):
    # Should always accept better states
    assert annealer.should_accept(new_energy=90, old_energy=100) is True

    # Test probabilistic acceptance for worse states
    annealer.temperature = 10.0
    np.random.seed(0) # for reproducibility
    # exp((100 - 101) / 10) = exp(-0.1) = 0.9048
    # np.random.rand() with seed 0 is 0.5488... < 0.9048, so should accept
    assert annealer.should_accept(new_energy=101, old_energy=100) is True

    # np.random.rand() with seed 0 is 0.5488, next is 0.7151...
    # Let's find a case where it's rejected
    # exp(-1) = 0.3678. Our random numbers are > this, so should be rejected.
    annealer.temperature = 1.0
    assert annealer.should_accept(new_energy=101, old_energy=100) is False

def test_update_phase_and_temperature_phase_a(annealer):
    annealer.initialize_state(MockQCState(energy=100))
    annealer.phase = "A"

    # Logarithmic cooling
    iteration = 10
    expected_temp = annealer.phase_a_cooling_const / np.log(iteration + 2)
    annealer._update_phase_and_temperature(iteration)

    assert annealer.phase == "A" # Should not switch yet
    assert annealer.temperature == pytest.approx(expected_temp)

def test_update_phase_and_temperature_phase_b(annealer):
    annealer.initialize_state(MockQCState(energy=100))
    annealer.phase = "B"
    initial_temp = 50.0
    annealer.temperature = initial_temp

    # Exponential cooling
    expected_temp = initial_temp * annealer.phase_b_cooling_rate
    annealer._update_phase_and_temperature(iteration=100) # iteration doesn't matter for phase B

    assert annealer.temperature == pytest.approx(expected_temp)

def test_check_phase_switch_false(annealer):
    # Not enough data
    annealer.energy_history = [100, 99, 98]
    assert annealer._check_phase_switch() is False

    # High variance
    annealer.energy_history = [100, 50, 150, 40, 160, 30, 170, 20, 180, 10] * 2
    assert annealer._check_phase_switch() is False

def test_check_phase_switch_true(annealer, annealer_config):
    # Low variance and negative median delta
    # Make variance small enough
    annealer_config["initial_temp"] = 10 # lower temp -> lower variance threshold
    annealer = TwoPhaseAnnealer(annealer_config)

    base_energy = 50
    # Create a list of slightly decreasing energies with low variance
    energies = [base_energy - i * 0.01 for i in range(annealer.phase_switch_window)]
    annealer.energy_history = energies

    assert annealer._check_phase_switch() is True

def test_full_phase_switch_logic(annealer):
    annealer.initialize_state(MockQCState(energy=100))

    # Simulate a run that should trigger a phase switch
    energies = [100 - i * 0.1 for i in range(annealer.phase_switch_window)]

    # Mock the check to return True
    annealer._check_phase_switch = lambda: True

    annealer._update_phase_and_temperature(iteration=50)

    assert annealer.phase == "B"
    # Check if temperature was reset for Phase B start
    assert annealer.temperature == annealer.initial_temp / 10.0

def test_check_convergence_false(annealer):
    # Not enough data
    annealer.energy_history = [100, 99, 98]
    assert annealer.check_convergence() is False

    # Energy still changing
    annealer.energy_history = [100] * 5 + [50] * 5
    annealer.phase = "B"
    annealer.temperature = annealer.min_temp
    assert annealer.check_convergence() == False

def test_check_convergence_true(annealer, annealer_config):
    annealer.phase = "B"
    annealer.temperature = annealer.min_temp

    # Flatlined energy
    annealer.energy_history = [50.0001, 50.0002, 50.00015] * (annealer.convergence_window // 3 + 1)

    assert annealer.check_convergence() == True
