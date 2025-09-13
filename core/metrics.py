# core/metrics.py

"""
Defines and computes various performance and quality metrics for the system.

These metrics serve as the classical foundation for the energy calculations
and the mapping to the quantum state. In a real system, these functions would
interface with static analysis tools, profilers, and code repository APIs.
For this implementation, they are placeholders that generate mock data.
"""

from __future__ import annotations

import random
from typing import Dict, Any

from core.data_models import SoftwareState

def compute_static_metrics(software_state: SoftwareState, raw_code_data: Dict[str, Any] = None) -> Dict[str, float]:
    """
    Computes static code metrics.

    This includes metrics like cyclomatic complexity, coupling between modules,
    and cohesion within modules.

    Args:
        software_state: The current software state.
        raw_code_data: Placeholder for raw data from static analysis tools.

    Returns:
        A dictionary of computed static metrics.
    """
    # Placeholder implementation: Generate random but plausible metric values.
    # The values could be loosely based on the number of components.
    num_components = len(software_state.component_versions)

    complexity = num_components * random.uniform(5, 15)
    coupling = num_components * (num_components - 1) * random.uniform(0.1, 0.5)
    cohesion = random.uniform(0.2, 0.9) # Cohesion is typically a ratio

    return {
        "cyclomatic_complexity": complexity,
        "coupling": coupling,
        "cohesion": cohesion,
    }

def compute_dynamic_metrics(software_state: SoftwareState, raw_runtime_data: Dict[str, Any] = None) -> Dict[str, float]:
    """
    Computes dynamic runtime metrics.

    This includes metrics like average response time, error rates, and memory usage.

    Args:
        software_state: The current software state.
        raw_runtime_data: Placeholder for raw data from profilers or monitoring systems.

    Returns:
        A dictionary of computed dynamic metrics.
    """
    # Placeholder implementation: Generate random but plausible values.
    # A 'degraded' status could lead to worse metrics.
    status_multiplier = 2.0 if software_state.status == 'degraded' else 1.0

    avg_response_time = status_multiplier * random.uniform(50, 200) # in ms
    peak_memory_usage = status_multiplier * random.uniform(512, 4096) # in MB
    error_rate = status_multiplier * random.uniform(0.001, 0.05) # as a fraction

    return {
        "avg_response_time": avg_response_time,
        "peak_memory_usage": peak_memory_usage,
        "error_rate": error_rate,
    }

def compute_interaction_metrics(software_state: SoftwareState, raw_dependency_data: Dict[str, Any] = None) -> Dict[str, float]:
    """
    Computes metrics related to inter-module interactions.

    This includes the number of dependencies and the size of API surfaces.

    Args:
        software_state: The current software state.
        raw_dependency_data: Placeholder for raw data from dependency graphs.

    Returns:
        A dictionary of computed interaction metrics.
    """
    # Placeholder implementation
    num_components = len(software_state.component_versions)

    # Assume dependencies scale with the number of components
    inter_module_dependencies = num_components * (num_components - 1) * random.uniform(0.2, 0.8)
    api_surface_area = num_components * random.uniform(10, 50) # e.g., number of API endpoints

    return {
        "inter_module_dependencies": inter_module_dependencies,
        "api_surface_area": api_surface_area,
    }

def collect_all_metrics(software_state: SoftwareState, raw_data: Dict[str, Any] = None) -> Dict[str, Dict[str, float]]:
    """
    A convenience function to collect all metrics for a given state.

    Args:
        software_state: The current software state.
        raw_data: A placeholder for all raw data sources.

    Returns:
        A nested dictionary containing all static, dynamic, and interaction metrics.
    """
    raw_data = raw_data or {}

    static = compute_static_metrics(software_state, raw_data.get('code'))
    dynamic = compute_dynamic_metrics(software_state, raw_data.get('runtime'))
    interaction = compute_interaction_metrics(software_state, raw_data.get('dependencies'))

    return {
        "static": static,
        "dynamic": dynamic,
        "interaction": interaction
    }

# Example Usage
if __name__ == '__main__':
    # Create a sample software state
    sw_state = SoftwareState(
        component_versions={"compA": "1.0", "compB": "2.1", "compC": "1.5"},
        config_hashes={"db": "hash123", "api": "hash456"},
        status="nominal"
    )

    print("--- Computing metrics for a nominal state ---")
    all_metrics = collect_all_metrics(sw_state)

    print("\nStatic Metrics:")
    for key, value in all_metrics['static'].items():
        print(f"  {key}: {value:.2f}")

    print("\nDynamic Metrics:")
    for key, value in all_metrics['dynamic'].items():
        print(f"  {key}: {value:.2f}")

    print("\nInteraction Metrics:")
    for key, value in all_metrics['interaction'].items():
        print(f"  {key}: {value:.2f}")

    # Create a degraded state to see the difference in dynamic metrics
    degraded_sw_state = SoftwareState(
        component_versions={"compA": "1.0", "compB": "2.1"},
        config_hashes={"db": "hash123"},
        status="degraded"
    )

    print("\n\n--- Computing metrics for a degraded state ---")
    degraded_metrics = collect_all_metrics(degraded_sw_state)

    print("\nDynamic Metrics (Degraded):")
    for key, value in degraded_metrics['dynamic'].items():
        print(f"  {key}: {value:.2f}")
