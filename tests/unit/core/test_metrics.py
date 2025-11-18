import pytest
from unittest.mock import patch
import numpy as np

from core.metrics import (
    compute_static_metrics,
    compute_dynamic_metrics,
    compute_interaction_metrics,
    collect_all_metrics,
)
from core.types import SoftwareState

@pytest.fixture
def nominal_state():
    return SoftwareState(
        component_versions={"compA": "1.0", "compB": "2.0"},
        config_hashes={"conf1": "hashA"},
        status="nominal"
    )

@pytest.fixture
def degraded_state():
    return SoftwareState(
        component_versions={"compA": "1.0", "compB": "2.0"},
        config_hashes={"conf1": "hashA"},
        status="degraded"
    )

def test_static_metrics_structure(nominal_state):
    """Tests the structure and types of the static metrics output."""
    metrics = compute_static_metrics(nominal_state)
    assert isinstance(metrics, dict)
    expected_keys = ["cyclomatic_complexity", "coupling", "cohesion"]
    assert all(key in metrics for key in expected_keys)
    assert all(isinstance(value, float) for value in metrics.values())

def test_dynamic_metrics_structure(nominal_state):
    """Tests the structure and types of the dynamic metrics output."""
    metrics = compute_dynamic_metrics(nominal_state)
    assert isinstance(metrics, dict)
    expected_keys = ["avg_response_time", "peak_memory_usage", "error_rate"]
    assert all(key in metrics for key in expected_keys)
    assert all(isinstance(value, float) for value in metrics.values())

def test_interaction_metrics_structure(nominal_state):
    """Tests the structure and types of the interaction metrics output."""
    metrics = compute_interaction_metrics(nominal_state)
    assert isinstance(metrics, dict)
    expected_keys = ["inter_module_dependencies", "api_surface_area"]
    assert all(key in metrics for key in expected_keys)
    assert all(isinstance(value, float) for value in metrics.values())

@patch('core.metrics.random.uniform')
def test_dynamic_metrics_degraded_multiplier(mock_uniform, nominal_state, degraded_state):
    """
    Tests that a 'degraded' status correctly applies a multiplier
    to dynamic metrics.
    """
    # Mock random.uniform to always return 1.0
    mock_uniform.return_value = 1.0

    # Metrics for nominal state
    nominal_metrics = compute_dynamic_metrics(nominal_state)
    assert nominal_metrics["avg_response_time"] == 1.0
    assert nominal_metrics["peak_memory_usage"] == 1.0
    assert nominal_metrics["error_rate"] == 1.0

    # Metrics for degraded state (should be multiplied by 2.0)
    degraded_metrics = compute_dynamic_metrics(degraded_state)
    assert degraded_metrics["avg_response_time"] == 2.0
    assert degraded_metrics["peak_memory_usage"] == 2.0
    assert degraded_metrics["error_rate"] == 2.0

def test_dynamic_metrics_degraded_statistically(nominal_state, degraded_state):
    """
    Tests that 'degraded' state metrics are statistically higher than 'nominal'.
    This is a more robust test against the randomness.
    """
    num_runs = 30
    nominal_means = {k: [] for k in ["avg_response_time", "peak_memory_usage", "error_rate"]}
    degraded_means = {k: [] for k in ["avg_response_time", "peak_memory_usage", "error_rate"]}

    for _ in range(num_runs):
        nominal_m = compute_dynamic_metrics(nominal_state)
        degraded_m = compute_dynamic_metrics(degraded_state)
        for key in nominal_means:
            nominal_means[key].append(nominal_m[key])
            degraded_means[key].append(degraded_m[key])

    # Check that the mean of degraded metrics is higher than for nominal
    for key in nominal_means:
        assert np.mean(degraded_means[key]) > np.mean(nominal_means[key])

def test_collect_all_metrics_structure(nominal_state):
    """Tests that collect_all_metrics returns a correctly structured dictionary."""
    all_metrics = collect_all_metrics(nominal_state)
    assert isinstance(all_metrics, dict)
    expected_top_keys = ["static", "dynamic", "interaction"]
    assert all(key in all_metrics for key in expected_top_keys)

    # Check that the sub-dictionaries have the correct structure
    assert "cyclomatic_complexity" in all_metrics["static"]
    assert "avg_response_time" in all_metrics["dynamic"]
    assert "api_surface_area" in all_metrics["interaction"]
