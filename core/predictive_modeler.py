from __future__ import annotations
import asyncio
from datetime import timedelta
from typing import List, Dict
import numpy as np

from core.data_models import PerformanceProfile, AppliedOptimization, PredictiveModel

class PredictivePerformanceModeler:
    """
    Creates predictive models for system performance based on historical data and optimizations.
    """

    async def create_mathematical_performance_model(
        self,
        historical_performance: PerformanceProfile,
        applied_optimizations: List[AppliedOptimization],
        prediction_horizon: timedelta,
    ) -> PredictiveModel:
        """
        Creates a simple predictive model based on the estimated impact of
        the applied optimizations.
        """
        await asyncio.sleep(0.1)  # Simulate async work

        # Find the baseline latency from the historical performance
        baseline_latency_metric = next(
            (m for m in historical_performance.baseline_metrics if m.name == "latency"), None
        )

        if not baseline_latency_metric:
            # Return a default model if latency is not being tracked
            return PredictiveModel(
                model_type="Default",
                equation="N/A",
                parameters={},
                prediction_horizon=prediction_horizon,
            )

        baseline_latency = baseline_latency_metric.value

        latency_per_energy_point = 0.2  # ms

        if not applied_optimizations:
            predicted_latency_reduction = 0.0
        else:
            # Reverse-engineer the initial energy from the baseline latency
            initial_energy = (baseline_latency - 50) / latency_per_energy_point

            # Get the final energy from the last applied optimization
            final_energy = applied_optimizations[-1].result.get("final_energy", initial_energy)

            actual_energy_reduction = initial_energy - final_energy
            predicted_latency_reduction = actual_energy_reduction * latency_per_energy_point
        predicted_future_latency = baseline_latency - predicted_latency_reduction

        # Create a simple descriptive model equation
        model_equation = (
            f"latency_pred = {baseline_latency:.2f} - {predicted_latency_reduction:.2f} "
            f"* (1 - exp(-t/τ))"
        )

        parameters = {
            "initial_latency": baseline_latency,
            "predicted_reduction": predicted_latency_reduction,
            "predicted_final_latency": predicted_future_latency,
            "tau_hours": prediction_horizon.total_seconds() / 3600,
        }

        return PredictiveModel(
            model_type="Exponential Decay to Target",
            equation=model_equation,
            parameters=parameters,
            prediction_horizon=prediction_horizon,
        )
