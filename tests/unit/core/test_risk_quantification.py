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
async def test_optimize_error_budget_allocation(risk_system, sample_system_state_low_risk):
    """
    Tests the (mocked) budget optimization logic.
    """
    from core.risk_quantification import ErrorBudgetAllocation

    current_alloc = ErrorBudgetAllocation(
        verified_surface_budget=0.01e-4,
        empirical_surface_budget=0.89e-4,
        security_surface_budget=0.1e-4,
        optimization_proof="",
        expected_risk_reduction=0
    )

    optimized_result = await risk_system.optimize_error_budget_allocation(current_alloc, sample_system_state_low_risk)

    assert optimized_result is not None
    assert optimized_result.improvement_factor > 1.0
    assert "Mock proof" in optimized_result.optimized_allocation.optimization_proof
