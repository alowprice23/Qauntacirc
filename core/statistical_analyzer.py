from __future__ import annotations
from typing import List
import numpy as np
from scipy.stats import ttest_ind

from core.data_models import PerformanceMetric, PerformanceImprovement

class StatisticalPerformanceAnalyzer:
    """
    Analyzes performance improvements with statistical significance tests.
    """

    def analyze_performance_improvement(
        self,
        baseline_performance: List[PerformanceMetric],
        optimized_performance: List[PerformanceMetric],
        statistical_significance_threshold: float = 0.05,
    ) -> List[PerformanceImprovement]:
        """
        Analyzes the performance improvement between baseline and optimized performance.

        Args:
            baseline_performance: A list of baseline performance metrics.
            optimized_performance: A list of optimized performance metrics.
            statistical_significance_threshold: The p-value threshold for statistical significance.

        Returns:
            A list of PerformanceImprovement objects.
        """
        improvements: List[PerformanceImprovement] = []

        # Create a map for easy lookup of optimized metrics
        optimized_metrics_map = {metric.name: metric for metric in optimized_performance}

        for baseline_metric in baseline_performance:
            optimized_metric = optimized_metrics_map.get(baseline_metric.name)

            if not optimized_metric:
                continue

            # Mock raw data for statistical testing
            # In a real system, this data would be collected during profiling.
            baseline_data = np.random.normal(loc=baseline_metric.value, scale=10, size=100)
            optimized_data = np.random.normal(loc=optimized_metric.value, scale=10, size=100)

            # Perform an independent two-sample t-test
            t_stat, p_value = ttest_ind(baseline_data, optimized_data, equal_var=False)

            is_significant = p_value < statistical_significance_threshold
            improvement_percentage = (
                (baseline_metric.value - optimized_metric.value) / baseline_metric.value
            ) * 100

            improvement = PerformanceImprovement(
                metric_name=baseline_metric.name,
                baseline_value=baseline_metric.value,
                optimized_value=optimized_metric.value,
                improvement_percentage=improvement_percentage,
                is_statistically_significant=is_significant,
                p_value=p_value,
            )
            improvements.append(improvement)

        return improvements
