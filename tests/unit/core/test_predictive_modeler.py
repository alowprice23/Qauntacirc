import pytest
from datetime import timedelta
from core.predictive_modeler import PredictivePerformanceModeler
from core.data_models import PerformanceProfile, PredictiveModel, PerformanceMetric, AppliedOptimization, OptimizationOpportunity

@pytest.mark.asyncio
async def test_create_mathematical_performance_model():
    modeler = PredictivePerformanceModeler()

    # Create a mock performance profile with a latency metric
    mock_performance_profile = PerformanceProfile(
        baseline_metrics=[
            PerformanceMetric(name="latency", value=100.0, unit="ms")
        ]
    )

    # Create a mock optimization
    mock_optimization = AppliedOptimization(
        opportunity=OptimizationOpportunity(
            id="OPT-1",
            description="Test opt",
            component_name="test",
            estimated_impact=50.0, # Corresponds to 10ms reduction
            mathematical_constraints=[]
        ),
        result={},
        mathematically_verified=True
    )

    predictive_model = await modeler.create_mathematical_performance_model(
        historical_performance=mock_performance_profile,
        applied_optimizations=[mock_optimization],
        prediction_horizon=timedelta(hours=1),
    )

    assert isinstance(predictive_model, PredictiveModel)
    assert predictive_model.model_type == "Exponential Decay to Target"
    assert "latency_pred" in predictive_model.equation
    assert "100.00" in predictive_model.equation # Initial latency
    assert "10.00" in predictive_model.equation # Predicted reduction
    assert predictive_model.parameters["initial_latency"] == 100.0
    assert predictive_model.parameters["predicted_reduction"] == 10.0
    assert predictive_model.parameters["predicted_final_latency"] == 90.0
