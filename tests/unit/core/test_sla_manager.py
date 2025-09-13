import pytest
import asyncio
from core.sla_manager import SLAMathematicalManager
from core.data_models import SystemState, SLARequirement, SLACompliance, PerformanceMetric

@pytest.mark.asyncio
async def test_verify_sla_compliance_with_bounds():
    manager = SLAMathematicalManager()
    mock_system_state = SystemState(
        id="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        timestamp="2023-10-27T10:00:00Z",
        software_state={},
        modules=[],
        requirements=[],
        energy_breakdown={"total": 100, "complexity": 20, "coupling": 30, "constraint": 10, "debt": 40},
        lyapunov_metrics={"phi": 120, "energy": 100, "test_penalty": 10, "obligation_penalty": 10}
    )

    sla_requirements = [
        SLARequirement(metric_name="latency", target_value=90, operator="<="),
        SLARequirement(metric_name="throughput", target_value=1000, operator=">="),
    ]

    compliance_results = await manager.verify_sla_compliance_with_bounds(
        optimized_system=mock_system_state,
        applied_optimizations=[],
        sla_requirements=sla_requirements,
        statistical_confidence=0.99,
    )

    assert isinstance(compliance_results, list)
    assert len(compliance_results) == 2
    assert all(isinstance(c, SLACompliance) for c in compliance_results)

    latency_compliance = next((c for c in compliance_results if c.requirement.metric_name == "latency"), None)
    assert latency_compliance is not None
    assert latency_compliance.is_compliant is True

    throughput_compliance = next((c for c in compliance_results if c.requirement.metric_name == "throughput"), None)
    assert throughput_compliance is not None
    assert throughput_compliance.is_compliant is True
