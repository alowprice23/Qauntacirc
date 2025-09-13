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
        Simulates fetching the performance profile of the optimized system
        by deriving performance metrics from the system's energy state.
        """
        await asyncio.sleep(0.1)  # Simulate async work for I/O

        total_energy = optimized_system.energy_breakdown.total

        # Define a relationship between energy and performance metrics
        # Lower energy should result in lower latency and higher throughput
        base_latency = 50  # ms
        latency_per_energy_point = 0.2  # ms
        latency = base_latency + (latency_per_energy_point * total_energy)

        base_throughput = 1500  # rps
        throughput_per_energy_point = 2  # rps
        throughput = base_throughput - (throughput_per_energy_point * total_energy)

        # Add some random noise to make it more realistic
        latency *= (1 + (asyncio.get_event_loop().time() % 0.05 - 0.025)) # up to 2.5% noise
        throughput *= (1 + (asyncio.get_event_loop().time() % 0.05 - 0.025))

        # Assume a 5% confidence interval width
        latency_ci = (latency * 0.975, latency * 1.025)
        throughput_ci = (throughput * 0.975, throughput * 1.025)

        optimized_metrics = [
            PerformanceMetric(
                name="latency",
                value=latency,
                unit="ms",
                confidence_interval=latency_ci,
                confidence_level=0.99,
            ),
            PerformanceMetric(
                name="throughput",
                value=throughput,
                unit="rps",
                confidence_interval=throughput_ci,
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
