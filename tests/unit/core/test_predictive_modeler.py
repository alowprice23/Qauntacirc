import pytest
import asyncio
from datetime import timedelta
from core.predictive_modeler import PredictivePerformanceModeler
from core.data_models import PerformanceProfile, PredictiveModel

@pytest.mark.asyncio
async def test_create_mathematical_performance_model():
    modeler = PredictivePerformanceModeler()
    mock_performance_profile = PerformanceProfile(baseline_metrics=[])

    predictive_model = await modeler.create_mathematical_performance_model(
        historical_performance=mock_performance_profile,
        applied_optimizations=[],
        prediction_horizon=timedelta(hours=1),
    )

    assert isinstance(predictive_model, PredictiveModel)
    assert predictive_model.model_type == "Linear Regression"
    assert "latency(t)" in predictive_model.equation
    assert "slope" in predictive_model.parameters
    assert "intercept" in predictive_model.parameters
