from __future__ import annotations
import asyncio
from typing import List, Dict

from core.data_models import (
    SystemState,
    AppliedOptimization,
    SLARequirement,
    SLACompliance,
    PerformanceMetric,
    PerformanceProfile,
)

class SLAMathematicalManager:
    """
    Manages and verifies Service Level Agreements (SLAs) with mathematical guarantees.
    """

    async def _get_optimized_performance(
        self,
        optimized_system: SystemState,
        applied_optimizations: List[AppliedOptimization],
    ) -> PerformanceProfile:
        """
        Simulates fetching the performance profile of the optimized system.
        In a real system, this would involve re-profiling the system after optimizations.
        """
        # Placeholder: For now, we'll assume the optimized system's performance is
        # slightly better than some baseline. Let's create a mock performance profile.
        await asyncio.sleep(0.1) # Simulate async work

        # Let's assume a 20% improvement in latency and 10% in throughput
        optimized_metrics = [
            PerformanceMetric(
                name="latency",
                value=80,
                unit="ms",
                confidence_interval=(75, 85),
                confidence_level=0.99,
            ),
            PerformanceMetric(
                name="throughput",
                value=1100,
                unit="rps",
                confidence_interval=(1050, 1150),
                confidence_level=0.99,
            ),
        ]
        return PerformanceProfile(baseline_metrics=optimized_metrics)


    async def verify_sla_compliance_with_bounds(
        self,
        optimized_system: SystemState,
        applied_optimizations: List[AppliedOptimization],
        sla_requirements: List[SLARequirement],
        statistical_confidence: float,
    ) -> List[SLACompliance]:
        """
        Verifies if the optimized system meets the SLA requirements with statistical confidence.

        Args:
            optimized_system: The state of the system after optimizations.
            applied_optimizations: The list of optimizations that were applied.
            sla_requirements: The list of SLA requirements to verify.
            statistical_confidence: The required confidence level for SLA compliance.

        Returns:
            A list of SLACompliance objects, one for each requirement.
        """
        optimized_performance = await self._get_optimized_performance(
            optimized_system, applied_optimizations
        )

        optimized_metrics_map: Dict[str, PerformanceMetric] = {
            metric.name: metric for metric in optimized_performance.baseline_metrics
        }

        compliance_results: List[SLACompliance] = []

        for requirement in sla_requirements:
            metric = optimized_metrics_map.get(requirement.metric_name)

            if not metric or metric.confidence_interval is None:
                compliance_results.append(
                    SLACompliance(
                        requirement=requirement,
                        measured_performance=metric,
                        is_compliant=False,
                        statistical_confidence=0.0,
                    )
                )
                continue

            lower_bound, upper_bound = metric.confidence_interval
            is_compliant = False

            if requirement.operator == "<=":
                # For a "<=" requirement to be met with confidence, the upper bound
                # of the confidence interval must be within the target.
                if upper_bound <= requirement.target_value:
                    is_compliant = True
            elif requirement.operator == ">=":
                # For a ">=" requirement, the lower bound must be above the target.
                if lower_bound >= requirement.target_value:
                    is_compliant = True
            elif requirement.operator == "==":
                 # For "==", the target must be within the confidence interval.
                if lower_bound <= requirement.target_value <= upper_bound:
                    is_compliant = True

            compliance_results.append(
                SLACompliance(
                    requirement=requirement,
                    measured_performance=metric,
                    is_compliant=is_compliant,
                    statistical_confidence=metric.confidence_level or statistical_confidence,
                )
            )

        return compliance_results
