import pytest
from agents.hydrospread.ops import forecast_code_growth
from core.data_models import TaskQuanta

def test_forecast_code_growth():
    tasks = [
        TaskQuanta(id="t1", description="d1", verification_criteria=["vc1"], energy=10.0),
        TaskQuanta(id="t2", description="d2", verification_criteria=["vc2"], energy=20.0),
    ]

    forecast = forecast_code_growth(tasks, viscosity=1.0, time_horizon=1.0)
    assert forecast > 0

    # Higher viscosity should lead to lower growth
    forecast_high_viscosity = forecast_code_growth(tasks, viscosity=2.0, time_horizon=1.0)
    assert forecast_high_viscosity < forecast

    # Longer time horizon should lead to higher growth
    forecast_long_horizon = forecast_code_growth(tasks, viscosity=1.0, time_horizon=2.0)
    assert forecast_long_horizon > forecast
