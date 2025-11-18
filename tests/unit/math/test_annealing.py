import pytest
import numpy as np
import math
from math_utils.annealing import TemperatureSchedule, GeometricCoolingSchedule, TwoPhaseAnnealer

def test_temperature_schedule_exponential():
    schedule = TemperatureSchedule(initial_temp=100, final_temp=1, steps=100, schedule_type='exponential')
    assert schedule.get_temperature(0) == 100
    assert schedule.get_temperature(100) == pytest.approx(1.0)
    assert schedule.get_temperature(50) < 100
    assert schedule.get_temperature(50) > 1

def test_temperature_schedule_logarithmic():
    schedule = TemperatureSchedule(initial_temp=100, final_temp=1, steps=100, schedule_type='logarithmic')
    assert schedule.get_temperature(0) == pytest.approx(100)
    assert schedule.get_temperature(1) == pytest.approx(100 * math.log(2) / math.log(3))

def test_temperature_schedule_linear():
    schedule = TemperatureSchedule(initial_temp=100, final_temp=1, steps=100, schedule_type='linear')
    assert schedule.get_temperature(0) == 100
    assert schedule.get_temperature(100) == pytest.approx(1.0)
    assert schedule.get_temperature(50) == pytest.approx(100 - (99/100)*50)

def test_temperature_schedule_invalid():
    schedule = TemperatureSchedule(schedule_type='invalid')
    with pytest.raises(ValueError):
        schedule.get_temperature(0)

def test_geometric_cooling_schedule():
    schedule = GeometricCoolingSchedule(initial_temp=100.0, cooling_rate=0.95, min_temp=0.1)
    assert schedule.initial_temp == 100.0
    assert schedule.cooling_rate == 0.95
    assert schedule.min_temp == 0.1

def test_two_phase_annealer_acceptance_probability():
    annealer = TwoPhaseAnnealer(lambda x: x, 0, TemperatureSchedule())
    assert annealer._acceptance_probability(10, 5, 100) == 1.0
    assert annealer._acceptance_probability(5, 10, 100) < 1.0
    assert annealer._acceptance_probability(5, 10, 100) > 0.0
    assert annealer._acceptance_probability(10, 10, 100) == np.exp(0)

def test_two_phase_annealer_simple_energy_function():
    # Define a simple quadratic energy function
    def energy_function(state):
        return np.sum(state**2)

    initial_state = np.array([10.0, -10.0])
    schedule = TemperatureSchedule(initial_temp=1000, final_temp=0.1, steps=2000, schedule_type='exponential')
    annealer = TwoPhaseAnnealer(energy_function, initial_state, schedule)

    best_state, best_energy = annealer.anneal()

    # The best state should be close to [0, 0]
    assert np.allclose(best_state, [0, 0], atol=1.0)
    assert best_energy < energy_function(initial_state)
    assert len(annealer.history) == 2000

def test_detect_phase_transition():
    annealer = TwoPhaseAnnealer(lambda x: x, 0, TemperatureSchedule())
    # Not enough data
    assert not annealer._detect_phase_transition([1, 2, 3])
    # Low variance
    assert not annealer._detect_phase_transition(np.ones(100))
    # High variance
    history = np.concatenate([np.ones(50), np.ones(50) * 10])
    assert annealer._detect_phase_transition(history)
