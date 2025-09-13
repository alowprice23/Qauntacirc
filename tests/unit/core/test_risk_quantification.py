import pytest
from core.risk_quantification import MathematicalRiskQuantificationSystem, SystemState

@pytest.fixture
def risk_system():
    """Fixture for the MathematicalRiskQuantificationSystem."""
    return MathematicalRiskQuantificationSystem(total_budget=1e-4)

@pytest.fixture
def sample_system_state_low_risk():
    """A sample system state representing a low-risk scenario."""
    return SystemState(
        formal_verification_results={"proofs": ["theorem1", "theorem2"]},
        total_statistical_tests=100000,
        observed_test_failures=1,
        chaos_test_results={"resilience_score": 0.99},
        penetration_test_results={"vulnerabilities": []}
    )

@pytest.fixture
def sample_system_state_high_risk():
    """A sample system state representing a high-risk scenario."""
    return SystemState(
        formal_verification_results={"proofs": []},
        total_statistical_tests=10000,
        observed_test_failures=50,
        chaos_test_results={"resilience_score": 0.7},
        penetration_test_results={"vulnerabilities": ["CVE-2024-XXXX"]}
    )

def test_risk_quantification_system_initialization(risk_system):
    """Tests that the system is initialized correctly."""
    assert risk_system is not None
    assert risk_system.total_budget == 1e-4
    assert "verified" in risk_system.error_budget_manager.budgets
    assert "empirical" in risk_system.error_budget_manager.budgets
    assert "security" in risk_system.error_budget_manager.budgets

def test_compute_comprehensive_risk_low_risk_scenario(risk_system, sample_system_state_low_risk):
    """
    Tests the comprehensive risk computation for a low-risk system state.
    """
    assessment = risk_system.compute_comprehensive_system_risk_bounds(sample_system_state_low_risk)

    # Check that the total risk is the sum of its parts
    assert assessment.total_system_risk == pytest.approx(
        assessment.verified_surface_risk +
        assessment.empirical_surface_risk +
        assessment.security_surface_risk
    )

    # Check that the system meets the budget
    assert assessment.meets_target_budget is True
    assert assessment.budget_compliance is True

    # Check certificate content
    assert "PASS" in assessment.mathematical_certificate
    assert "Total System Risk Bound" in assessment.mathematical_certificate
    assert "Tighter Chernoff Bound Calculation" in assessment.mathematical_certificate

def test_compute_comprehensive_risk_high_risk_scenario(risk_system, sample_system_state_high_risk):
    """
    Tests the comprehensive risk computation for a high-risk system state.
    """
    assessment = risk_system.compute_comprehensive_system_risk_bounds(sample_system_state_high_risk)

    # Check that the total risk is the sum of its parts
    assert assessment.total_system_risk == pytest.approx(
        assessment.verified_surface_risk +
        assessment.empirical_surface_risk +
        assessment.security_surface_risk
    )

    # In this scenario, we expect the risk to be higher and likely fail the budget
    # With the new bound, p_upper is ~0.0065, which is >> 1e-4.
    assert assessment.total_system_risk > 1e-4
    assert assessment.meets_target_budget is False
    assert assessment.budget_compliance is False

    # Check certificate content
    assert "FAIL" in assessment.mathematical_certificate
    assert "Total System Risk Bound" in assessment.mathematical_certificate
    assert "Tighter Chernoff Bound Calculation" in assessment.mathematical_certificate

@pytest.mark.asyncio
async def test_optimize_error_budget_allocation_real(risk_system, sample_system_state_high_risk):
    """
    Tests the real budget optimization logic.
    We use the high-risk scenario as it provides a better case for optimization.
    """
    from core.risk_quantification import ErrorBudgetAllocation
    import numpy as np

    # Start with a non-optimal allocation (e.g., equal split)
    total_budget = risk_system.total_budget
    initial_budget_per_surface = total_budget / 3.0

    current_alloc = ErrorBudgetAllocation(
        verified_surface_budget=initial_budget_per_surface,
        empirical_surface_budget=initial_budget_per_surface,
        security_surface_budget=initial_budget_per_surface,
        optimization_proof="Initial equal allocation.",
        expected_risk_reduction=0
    )

    # Run the optimization
    optimized_result = await risk_system.optimize_error_budget_allocation(current_alloc, sample_system_state_high_risk)

    # 1. Check the output is valid
    assert optimized_result is not None
    assert isinstance(optimized_result.optimized_allocation, ErrorBudgetAllocation)

    # 2. Check that the new budget allocation is valid and sums to the total budget
    new_alloc = optimized_result.optimized_allocation
    total_allocated_budget = new_alloc.verified_surface_budget + new_alloc.empirical_surface_budget + new_alloc.security_surface_budget
    assert np.isclose(total_allocated_budget, total_budget)

    # 3. Check that the optimization actually improved the situation
    # In a high-risk scenario, we expect a significant improvement
    assert optimized_result.improvement_factor > 1.0
    assert new_alloc.expected_risk_reduction > 0

    # 4. Check that the proofs are no longer mocked
    assert "Mock proof" not in new_alloc.optimization_proof
    assert "SLSQP solver" in new_alloc.optimization_proof
    assert "Mock optimality" not in optimized_result.mathematical_optimality_certificate
    assert "Karush-Kuhn-Tucker" in optimized_result.mathematical_optimality_certificate
