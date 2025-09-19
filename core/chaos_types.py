from typing import List, Dict, Any, Callable
from pydantic import BaseModel
from core.types import PhysicsResult

class ChaosScenario(BaseModel):
    """Defines a chaos testing scenario."""
    name: str
    description: str
    target_components: List[str]
    fault_injection: Callable
    expected_behavior: str
    recovery_criteria: Dict[str, Any]
    blast_radius: float  # 0.0 to 1.0
    duration_seconds: int

    class Config:
        arbitrary_types_allowed = True

class ChaosTestingPlan(BaseModel):
    """Defines a plan for executing a series of chaos tests."""
    scenarios: List[ChaosScenario]
    execution_order: List[int]
    monitoring_setup: Dict[str, Any]
    recovery_procedures: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

class ResilienceReport(BaseModel):
    """Represents the resilience report of a chaos experiment."""
    scenario_name: str
    baseline_metrics: Dict[str, Any]
    chaos_metrics: Dict[str, Any]
    recovery_metrics: Dict[str, Any]
    resilience_score: float
    recovery_time: float
    sla_violations: int
    data_consistency_maintained: bool
    recommendations: List[str]

    class Config:
        arbitrary_types_allowed = True

class ChaosPlanResult(PhysicsResult):
    """The result of the FluctuaTest agent, containing a plan."""
    chaos_plan: ChaosTestingPlan

    class Config:
        arbitrary_types_allowed = True
