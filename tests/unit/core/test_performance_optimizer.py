import pytest
from unittest.mock import patch
from core.performance_optimizer import PhysicsBasedPerformanceOptimizer
from core.data_models import SystemState, PerformanceProfile, SLARequirement, OptimizationOpportunity, EnergyBreakdown, LyapunovMetrics

@patch('core.performance_optimizer.EnergyCalculator')
def test_identify_optimization_opportunities(MockEnergyCalculator):
    # Configure the mock
    mock_energy_calculator_instance = MockEnergyCalculator.return_value
    mock_energy_calculator_instance.compute_total_energy.return_value = EnergyBreakdown(
        total=100, complexity=20, coupling=50, constraint=10, debt=20
    )

    optimizer = PhysicsBasedPerformanceOptimizer()
    # Replace the optimizer's calculator with the mock instance
    optimizer.energy_calculator = mock_energy_calculator_instance

    # Create a mock SystemState
    mock_system_state = SystemState(
        id="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        timestamp="2023-10-27T10:00:00Z",
        software_state={},
        modules=[],
        requirements=[],
        energy_breakdown=EnergyBreakdown(total=0, complexity=0, coupling=0, constraint=0, debt=0), # This will be ignored
        lyapunov_metrics=LyapunovMetrics(phi=120, energy=100, test_penalty=10, obligation_penalty=10)
    )

    mock_performance_profile = PerformanceProfile(baseline_metrics=[])
    mock_sla_requirements = []

    opportunities = optimizer.identify_optimization_opportunities(
        performance_profile=mock_performance_profile,
        system_state=mock_system_state,
        sla_requirements=mock_sla_requirements,
    )

    assert isinstance(opportunities, list)
    assert len(opportunities) == 1
    assert isinstance(opportunities[0], OptimizationOpportunity)
    assert opportunities[0].id == "OPT-COUPLING-001"
