"""
Demonstration script for the MathematicalRiskQuantificationSystem.

This script showcases the capabilities of the system by running it through
several scenarios:
1. A low-risk state where the system easily meets its risk budget.
2. A high-risk state that violates the budget.
3. Optimization of the risk budget in the high-risk state to improve allocation.
4. A simulation of real-time monitoring where risk increases as new failures are observed.
"""
import asyncio
import textwrap
import sys

# This script requires the project's core modules.
sys.path.append('.')

from core.risk_quantification import (
    MathematicalRiskQuantificationSystem,
    SystemState,
    ErrorBudgetAllocation
)


def print_header(title):
    """Prints a formatted header for each scenario."""
    print("\n" + "="*80)
    print(f"| {title.upper():^76} |")
    print("="*80)

def print_assessment(assessment):
    """Prints a formatted summary of a risk assessment."""
    print(f"  -> Total System Risk: {assessment.total_system_risk:.6e}")
    print(f"  -> Meets Target Budget (<= 1e-4): {'YES' if assessment.meets_target_budget else 'NO'}")
    print("\n" + textwrap.indent(assessment.mathematical_certificate, "  "))


async def main():
    """Main function to run the demonstration scenarios."""
    # Instantiate the system with a total risk budget of 10⁻⁴
    risk_system = MathematicalRiskQuantificationSystem(total_budget=1e-4)

    # --- Scenario 1: Low-Risk System State ---
    print_header("Scenario 1: Low-Risk System State Assessment")

    low_risk_state = SystemState(
        formal_verification_results={"proofs": ["theorem_stability", "theorem_correctness"]},
        total_statistical_tests=1_000_000,
        observed_test_failures=2,
        chaos_test_results={"resilience_score": 0.995},
        penetration_test_results={"vulnerabilities": []}
    )

    print("Running assessment for a low-risk system state...")
    low_risk_assessment = risk_system.compute_comprehensive_system_risk_bounds(low_risk_state)

    print_assessment(low_risk_assessment)
    print("\nCONCLUSION: The system's risk is well within the 10⁻⁴ budget.")

    # --- Scenario 2: High-Risk Scenario and Budget Optimization ---
    print_header("Scenario 2: High-Risk Scenario & Budget Optimization")

    high_risk_state = SystemState(
        formal_verification_results={"proofs": []},
        total_statistical_tests=50_000,
        observed_test_failures=150,
        chaos_test_results={"resilience_score": 0.85},
        penetration_test_results={"vulnerabilities": ["CVE-2024-CRITICAL"]}
    )

    print("Running assessment for a high-risk system state...")
    high_risk_assessment = risk_system.compute_comprehensive_system_risk_bounds(high_risk_state)
    print_assessment(high_risk_assessment)
    print("\nCONCLUSION: The system's risk is far above the 10⁻⁴ budget. Action is required.")

    print("\n--- Initiating Budget Optimization ---")
    initial_allocation = ErrorBudgetAllocation(
        verified_surface_budget=risk_system.total_budget / 3,
        empirical_surface_budget=risk_system.total_budget / 3,
        security_surface_budget=risk_system.total_budget / 3,
        optimization_proof="Initial equal allocation.",
        expected_risk_reduction=0
    )
    print("Initial (non-optimal) budget allocation:")
    print(f"  - Verified: {initial_allocation.verified_surface_budget:.2e}, Empirical: {initial_allocation.empirical_surface_budget:.2e}, Security: {initial_allocation.security_surface_budget:.2e}")

    optimized_result = await risk_system.optimize_error_budget_allocation(initial_allocation, high_risk_state)
    new_alloc = optimized_result.optimized_allocation

    print("\nOptimized budget allocation recommendation:")
    print(f"  - Verified: {new_alloc.verified_surface_budget:.2e}, Empirical: {new_alloc.empirical_surface_budget:.2e}, Security: {new_alloc.security_surface_budget:.2e}")
    print(f"\n  -> Expected Improvement Factor: {optimized_result.improvement_factor:.2f}x")
    print(f"  -> Expected Risk Reduction: {new_alloc.expected_risk_reduction:.6e}")
    print("\n" + textwrap.indent(optimized_result.mathematical_optimality_certificate, "  "))
    print("\nCONCLUSION: The optimizer suggests reallocating budget towards the empirical and security surfaces,")
    print("where it will be most effective at reducing the overall system risk.")

    # --- Scenario 3: Real-Time Monitoring Simulation ---
    print_header("Scenario 3: Real-Time Monitoring Simulation")
    print("Simulating a system over time as new test failures are observed...")

    monitored_state = SystemState(
        formal_verification_results={"proofs": ["theorem_stability"]},
        total_statistical_tests=1_000_000,
        observed_test_failures=10,
        chaos_test_results={"resilience_score": 0.99},
        penetration_test_results={"vulnerabilities": []}
    )

    for i in range(5):
        new_failures = 25 * (i + 1)
        monitored_state.observed_test_failures += new_failures

        print(f"\n--- Day {i+1}: {new_failures} new failures observed (Total: {monitored_state.observed_test_failures}) ---")

        assessment = risk_system.compute_comprehensive_system_risk_bounds(monitored_state)

        print(f"  -> New Total System Risk: {assessment.total_system_risk:.6e}")
        if not assessment.meets_target_budget:
            print("  !! ALERT: Total system risk has EXCEEDED the 1e-4 budget. !!")

    print("\nCONCLUSION: The risk quantification system can be used for real-time monitoring")
    print("to track risk evolution and trigger alerts when the budget is violated.")


if __name__ == "__main__":
    asyncio.run(main())
