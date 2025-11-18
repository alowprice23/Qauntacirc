# Tests for the EnergyCalculator class
import pytest
import numpy as np
from core.energy_calculator import EnergyCalculator
from core.types import QCState, EnergyComponents, SoftwareState
from math_utils.annealing import GeometricCoolingSchedule

# Helper to create valid QCState objects for tests
def create_mock_qc_state(energy_components: EnergyComponents, potential: float = 0.1, contraction: float = 0.5) -> QCState:
    mock_software_state = SoftwareState(
        component_versions={"test_component": "1.0"},
        config_hashes={"test_config": "hash123"},
        status="test"
    )
    return QCState(
        software_state=mock_software_state,
        energy=energy_components.total,
        energy_components=energy_components,
        lyapunov_potential=potential,
        contraction_factor=contraction
    )

# Test initialization and configuration
def test_initialization_default_weights():
    calculator = EnergyCalculator()
    assert calculator._w_complexity == 1.0
    assert calculator._w_coupling == 1.5

def test_initialization_custom_weights():
    config = {"w_complexity": 2.5, "w_coupling": 3.0}
    calculator = EnergyCalculator(config)
    assert calculator._w_complexity == 2.5
    assert calculator._w_coupling == 3.0

# Test individual energy component calculations
def test_compute_static_energy():
    calculator = EnergyCalculator()
    metrics = {'cyclomatic_complexity': 10, 'coupling': 5, 'cohesion': 0.8}
    expected_energy = (1.0 * 10) + (1.5 * 5) - (1.2 * (1 / (0.8 + 1e-6)))
    assert calculator.compute_static_energy(metrics) == pytest.approx(expected_energy)

def test_compute_dynamic_energy():
    calculator = EnergyCalculator()
    metrics = {'avg_response_time': 50, 'peak_memory_usage': 1024}
    expected_energy = (2.0 * 50) + (1.8 * 1024)
    assert calculator.compute_dynamic_energy(metrics) == pytest.approx(expected_energy)

def test_compute_interaction_energy():
    calculator = EnergyCalculator()
    metrics = {'inter_module_dependencies': 20, 'api_surface_area': 15}
    expected_energy = (1.3 * 20) + (1.1 * 15)
    assert calculator.compute_interaction_energy(metrics) == pytest.approx(expected_energy)

# Test total energy calculation
def test_compute_total_energy():
    calculator = EnergyCalculator()
    static_metrics = {'cyclomatic_complexity': 10, 'coupling': 5, 'cohesion': 0.8}
    dynamic_metrics = {'avg_response_time': 50, 'peak_memory_usage': 1024}
    interaction_metrics = {'inter_module_dependencies': 20, 'api_surface_area': 15}

    e_static = calculator.compute_static_energy(static_metrics)
    e_dynamic = calculator.compute_dynamic_energy(dynamic_metrics)
    e_interaction = calculator.compute_interaction_energy(interaction_metrics)

    total_energy, components = calculator.compute_total_energy(static_metrics, dynamic_metrics, interaction_metrics)

    assert total_energy == pytest.approx(e_static + e_dynamic + e_interaction)
    assert components.static == e_static
    assert components.dynamic == e_dynamic
    assert components.interaction == e_interaction

# Test gradient and Hessian calculations
def test_energy_gradient_and_hessian():
    # We are using a simplified mock for state changes, so we test the numerical
    # differentiation logic rather than the physical meaning.
    calculator = EnergyCalculator()
    energy_components = EnergyComponents(static=10.0, dynamic=20.0, interaction=5.0)
    # Mocking QCState and its relevant attributes
    mock_state = create_mock_qc_state(energy_components)

    # The mock _recompute_energy_from_params is linear, so gradient should be [1, 1, 1]
    # and Hessian should be all zeros.
    gradient = calculator.energy_gradient(mock_state)
    hessian = calculator.energy_hessian(mock_state)

    assert np.allclose(gradient, [1.0, 1.0, 1.0])
    assert np.allclose(hessian, np.zeros((3, 3)))

# Test stability check integration
def test_check_stability_with_lyapunov():
    calculator = EnergyCalculator()
    # A state with a non-zero gradient should be considered stable by this proxy
    stable_components = EnergyComponents(static=10.0, dynamic=20.0, interaction=5.0)
    mock_stable_state = create_mock_qc_state(stable_components)

    # We need to adjust the mock to produce a zero gradient
    original_recompute = calculator._recompute_energy_from_params
    def mock_recompute_for_stability(params):
        # Let's make the energy quadratic so the gradient isn't always constant
        # E = p0^2 + p1^2 + p2^2. Gradient is [2*p0, 2*p1, 2*p2].
        components = EnergyComponents(static=params[0], dynamic=params[1], interaction=params[2])
        total_energy = params[0]**2 + params[1]**2 + params[2]**2
        return total_energy, components

    calculator._recompute_energy_from_params = mock_recompute_for_stability

    assert calculator.check_stability_with_lyapunov(mock_stable_state) == True

    # A zero gradient state would be unstable by this check
    zero_grad_components = EnergyComponents(static=0.0, dynamic=0.0, interaction=0.0)
    # The mock _recompute_energy_from_params uses the components as parameters.
    # To get a zero gradient from our quadratic mock, the params must be zero.
    mock_zero_grad_state = create_mock_qc_state(zero_grad_components)
    assert calculator.check_stability_with_lyapunov(mock_zero_grad_state) == False

    # Restore original method
    calculator._recompute_energy_from_params = original_recompute

# Test annealing schedule creation
def test_get_annealing_schedule():
    calculator = EnergyCalculator()
    schedule = calculator.get_annealing_schedule(100, 1, 0.95)
    assert isinstance(schedule, GeometricCoolingSchedule)
    assert schedule.initial_temp == 100
    assert schedule.min_temp == 1
    assert schedule.cooling_rate == 0.95
