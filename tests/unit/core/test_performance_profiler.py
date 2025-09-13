import pytest
import asyncio
from core.performance_profiler import MathematicalPerformanceProfiler
from core.data_models import SystemState, PerformanceProfile, PerformanceMetric

@pytest.mark.asyncio
async def test_profile_with_statistical_bounds():
    profiler = MathematicalPerformanceProfiler()
    # Create a mock SystemState
    mock_system_state = SystemState(
        id="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        timestamp="2023-10-27T10:00:00Z",
        software_state={},
        modules=[],
        requirements=[],
        energy_breakdown={"total": 100, "complexity": 20, "coupling": 30, "constraint": 10, "debt": 40},
        lyapunov_metrics={"phi": 120, "energy": 100, "test_penalty": 10, "obligation_penalty": 10}
    )


    profile = await profiler.profile_with_statistical_bounds(
        system=mock_system_state,
        measurement_duration=0.1,
        confidence_level=0.95
    )

    assert isinstance(profile, PerformanceProfile)
    assert len(profile.baseline_metrics) == 2

    latency_metric = next((m for m in profile.baseline_metrics if m.name == "latency"), None)
    assert latency_metric is not None
    assert latency_metric.unit == "ms"
    assert latency_metric.confidence_level == 0.95
    assert latency_metric.confidence_interval is not None

    throughput_metric = next((m for m in profile.baseline_metrics if m.name == "throughput"), None)
    assert throughput_metric is not None
    assert throughput_metric.unit == "rps"
    assert throughput_metric.confidence_level == 0.95
    assert throughput_metric.confidence_interval is not None
