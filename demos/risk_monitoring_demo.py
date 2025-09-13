import asyncio
import datetime
import time
import math
from core.risk_quantification import MathematicalRiskQuantificationSystem, SystemState, ErrorBudgetAllocation

async def main():
    """
    Demonstrates the Mathematical Risk Quantification System in a simulated
    real-time monitoring scenario.
    """
    print("--- Real-Time Risk Monitoring and Budget Optimization Demo ---")

    # 1. Initialize the system
    risk_system = MathematicalRiskQuantificationSystem(total_budget=1e-4)

    # 2. Define the initial state of the system (starting in a relatively high-risk state)
    system_state = SystemState(
        formal_verification_results={"proofs": []},
        total_statistical_tests=5000,
        observed_test_failures=10,
        chaos_test_results={"resilience_score": 0.8},
        penetration_test_results={"vulnerabilities": ["CVE-2024-YYYY"]}
    )

    # Start with a non-optimal, equal budget allocation
    initial_budget = risk_system.total_budget / 3.0
    current_allocation = ErrorBudgetAllocation(
        verified_surface_budget=initial_budget,
        empirical_surface_budget=initial_budget,
        security_surface_budget=initial_budget,
        optimization_proof="Initial equal allocation.",
        expected_risk_reduction=0
    )

    # 3. Run the monitoring loop for a few cycles
    for i in range(5):
        print(f"\n--- Cycle {i+1} at {datetime.datetime.now().isoformat()} ---")

        # a. Compute and display the current system risk
        print("Assessing current system risk...")
        risk_assessment = risk_system.compute_comprehensive_system_risk_bounds(system_state)

        print(f"  - Verified Surface Risk:  {risk_assessment.verified_surface_risk:.6e}")
        print(f"  - Empirical Surface Risk: {risk_assessment.empirical_surface_risk:.6e}")
        print(f"  - Security Surface Risk:  {risk_assessment.security_surface_risk:.6e}")
        print(f"  - Total System Risk:      {risk_assessment.total_system_risk:.6e}")
        print(f"  - Meets Target (<= {risk_system.total_budget:.0e}): {'YES' if risk_assessment.meets_target_budget else 'NO'}")

        # b. Optimize budget allocation based on the current state
        print("\nOptimizing error budget allocation...")
        try:
            optimized_result = await risk_system.optimize_error_budget_allocation(current_allocation, system_state)
            new_allocation = optimized_result.optimized_allocation

            print("  - Optimization successful!")
            print(f"  - Expected Improvement Factor: {optimized_result.improvement_factor:.2f}x")
            print(f"  - Expected Risk Reduction: {new_allocation.expected_risk_reduction:.6e}")
            print("\n  Optimized Budget Allocation:")
            print(f"    - Verified Surface: {new_allocation.verified_surface_budget:.6e} ({(new_allocation.verified_surface_budget/risk_system.total_budget)*100:.1f}%)")
            print(f"    - Empirical Surface: {new_allocation.empirical_surface_budget:.6e} ({(new_allocation.empirical_surface_budget/risk_system.total_budget)*100:.1f}%)")
            print(f"    - Security Surface: {new_allocation.security_surface_budget:.6e} ({(new_allocation.security_surface_budget/risk_system.total_budget)*100:.1f}%)")

            # Update the current allocation for the next cycle
            current_allocation = new_allocation

        except RuntimeError as e:
            print(f"  - Optimization failed: {e}")

        # c. Simulate system evolution for the next cycle
        print("\nSimulating system evolution for next cycle...")
        # More tests are run, hopefully reducing the empirical risk
        system_state.total_statistical_tests += 20000
        # Let's say we fix some bugs
        system_state.observed_test_failures += math.floor(20000 * (system_state.observed_test_failures / system_state.total_statistical_tests) * 0.5) # fewer new failures
        # A new formal proof is added
        system_state.formal_verification_results["proofs"].append(f"theorem_cycle_{i+1}")

        # Pause to make the simulation feel real-time
        time.sleep(2)

    print("\n--- Demo Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
