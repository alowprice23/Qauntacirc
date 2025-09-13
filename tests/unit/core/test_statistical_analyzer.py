import pytest
from core.statistical_analyzer import StatisticalPerformanceAnalyzer
from core.data_models import PerformanceMetric, PerformanceImprovement

def test_analyze_performance_improvement():
    analyzer = StatisticalPerformanceAnalyzer()
    baseline_metrics = [
        PerformanceMetric(name="latency", value=120, unit="ms"),
        PerformanceMetric(name="throughput", value=900, unit="rps"),
    ]
    optimized_metrics = [
        PerformanceMetric(name="latency", value=100, unit="ms"),
        PerformanceMetric(name="throughput", value=1100, unit="rps"),
    ]

    improvements = analyzer.analyze_performance_improvement(
        baseline_performance=baseline_metrics,
        optimized_performance=optimized_metrics,
        statistical_significance_threshold=0.05,
    )

    assert isinstance(improvements, list)
    assert len(improvements) == 2
    assert all(isinstance(i, PerformanceImprovement) for i in improvements)

    latency_improvement = next((i for i in improvements if i.metric_name == "latency"), None)
    assert latency_improvement is not None
    assert latency_improvement.is_statistically_significant is True
    assert latency_improvement.improvement_percentage > 15

    throughput_improvement = next((i for i in improvements if i.metric_name == "throughput"), None)
    assert throughput_improvement is not None
    assert throughput_improvement.is_statistically_significant is True
    assert throughput_improvement.improvement_percentage > 20
