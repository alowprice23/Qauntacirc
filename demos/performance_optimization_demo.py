import asyncio
from datetime import datetime, timedelta

from core.data_models import (
    SystemState,
    SLARequirement,
    Module,
    EnergyBreakdown,
    LyapunovMetrics,
    SoftwareState,
)
from core.performance_optimizer import MathematicalPerformanceOptimizationSystem


async def main():
    """
    A simple demonstration of the MathematicalPerformanceOptimizationSystem.
    """
    print("--- Performance Optimization System Demo ---")

    # 1. Setup: Create a mock SystemState
    mock_modules = [
        Module(
            name="module1",
            normalized_ast=b"...",
            semantic_tokens=["a", "b", "c"],
            cyclomatic_complexity=10,
            duplication_factor=0.2,
            coverage_deficit=0.3,
            last_refactor=datetime.utcnow() - timedelta(days=100),
        ),
        Module(
            name="module2",
            normalized_ast=b"...",
            semantic_tokens=["d", "e", "f"],
            cyclomatic_complexity=5,
            duplication_factor=0.1,
            coverage_deficit=0.1,
            last_refactor=datetime.utcnow() - timedelta(days=20),
        ),
    ]

    mock_system_state = SystemState(
        software_state=SoftwareState(),
        modules=mock_modules,
        energy_breakdown=EnergyBreakdown(
            total=250, complexity=100, coupling=80, constraint=20, debt=50
        ),
        lyapunov_metrics=LyapunovMetrics(
            phi=300, energy=250, test_penalty=30, obligation_penalty=20
        ),
    )

    # 2. Instantiate the System
    optimizer_system = MathematicalPerformanceOptimizationSystem()

    # 3. Define SLAs
    sla_requirements = [
        SLARequirement(metric_name="latency", target_value=90, operator="<="),
        SLARequirement(metric_name="throughput", target_value=1050, operator=">="),
    ]
    print(f"\nTarget SLAs: {sla_requirements}")

    # 4. Run Optimization
    print("\nRunning performance optimization...")
    result = await optimizer_system.optimize_system_performance_with_mathematical_guarantees(
        system=mock_system_state, sla_requirements=sla_requirements
    )
    print("Optimization complete.")

    # 5. Print Results
    print("\n--- Optimization Results ---")
    print(f"\nBaseline Performance:")
    for metric in result.baseline_performance.baseline_metrics:
        print(f"  - {metric.name}: {metric.value:.2f} {metric.unit} (95% CI: {metric.confidence_interval})")

    print(f"\nApplied Optimizations:")
    for opt in result.applied_optimizations:
        print(f"  - {opt.opportunity.id}: {opt.opportunity.description}")

    print(f"\nSLA Compliance:")
    for compliance in result.sla_compliance:
        status = "Compliant" if compliance.is_compliant else "Not Compliant"
        print(
            f"  - {compliance.requirement.metric_name}: {status} "
            f"(Confidence: {compliance.statistical_confidence:.2f})"
        )

    print(f"\nPredictive Model:")
    print(f"  - Type: {result.predictive_model.model_type}")
    print(f"  - Equation: {result.predictive_model.equation}")

    print(f"\nPerformance Improvement Analysis:")
    for improvement in result.improvement_analysis:
        print(
            f"  - {improvement.metric_name}: {improvement.improvement_percentage:.2f}% improvement "
            f"(p-value: {improvement.p_value:.4f}, "
            f"Significant: {improvement.is_statistically_significant})"
        )

    print(f"\nOverall SLA Compliance: {'Yes' if result.meets_all_sla_requirements else 'No'}")
    print(f"\nMathematical Performance Certificate: {result.mathematical_performance_certificate}")


if __name__ == "__main__":
    asyncio.run(main())
