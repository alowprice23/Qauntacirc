from __future__ import annotations
import asyncio
from datetime import datetime
from typing import List
import numpy as np

from core.data_models import SystemState, PerformanceProfile, PerformanceMetric
from math_utils.uncertainty_bounds import bootstrap_confidence_interval

class MathematicalPerformanceProfiler:
    """Profiles system performance with mathematical and statistical rigor."""

    async def _collect_performance_data(self, system: SystemState, duration: float) -> dict[str, np.ndarray]:
        """
        Simulates the collection of performance data over a given duration
        by deriving performance metrics from the system's energy state.
        """
        await asyncio.sleep(duration)  # Simulate the measurement period

        total_energy = system.energy_breakdown.total

        # Define a deterministic relationship between energy and performance metrics
        # Lower energy should result in lower latency and higher throughput
        base_latency = 50
        latency_per_energy_point = 0.2
        mean_latency = base_latency + (latency_per_energy_point * total_energy)

        base_throughput = 1500
        throughput_per_energy_point = 2
        mean_throughput = base_throughput - (throughput_per_energy_point * total_energy)

        # Generate a stable dataset based on these means
        latency_data = np.random.normal(loc=mean_latency, scale=mean_latency * 0.05, size=100)
        throughput_data = np.random.normal(loc=mean_throughput, scale=mean_throughput * 0.05, size=100)

        return {
            "latency": latency_data,
            "throughput": throughput_data,
        }

    async def profile_with_statistical_bounds(
        self, system: SystemState, measurement_duration: float, confidence_level: float
    ) -> PerformanceProfile:
        """
        Profiles the system's performance and calculates statistical bounds for the metrics.

        Args:
            system: The current state of the system.
            measurement_duration: The duration in seconds to collect performance data.
            confidence_level: The desired confidence level for the statistical bounds.

        Returns:
            A PerformanceProfile object containing the measured performance metrics.
        """
        raw_performance_data = await self._collect_performance_data(system, measurement_duration)

        performance_metrics: List[PerformanceMetric] = []
        alpha = 1.0 - confidence_level

        for metric_name, data in raw_performance_data.items():
            mean_value = np.mean(data)
            confidence_interval = bootstrap_confidence_interval(data, alpha=alpha)

            unit = "ms" if metric_name == "latency" else "rps"

            metric = PerformanceMetric(
                name=metric_name,
                value=mean_value,
                unit=unit,
                confidence_interval=confidence_interval,
                confidence_level=confidence_level,
            )
            performance_metrics.append(metric)

        return PerformanceProfile(baseline_metrics=performance_metrics)
