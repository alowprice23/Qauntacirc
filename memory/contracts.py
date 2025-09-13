"""
This file contains data structures for memory-agent communication.
"""
from pydantic import BaseModel
from typing import List, Any, Dict, Optional

from memory.types import FactNode
from core.data_models import AgentAction, SystemState

class MemoryGuidance(BaseModel):
    """Guidance provided by the memory system to an agent."""
    patterns: List[Any] # Should be List[Pattern] but Pattern is not defined yet
    recommendations: List[str]
    mathematical_justification: str
    confidence: float
    risk_assessment: Dict[str, Any]

class MemoryUpdate(BaseModel):
    """An update to be sent to the memory system after an action."""
    pattern_node: FactNode
    memory_delta: float
    learning_certificate: str

class ActionResult(BaseModel):
    """The result of an agent's action."""
    success_metrics: Dict[str, float]
    energy_delta: float
    convergence_metrics: Dict[str, float]
    # Adding fields from ExecutionResult to make it compatible
    success: bool
    confidence: float

class LearningPattern(BaseModel):
    action: AgentAction
    result: ActionResult
    mathematical_properties: Dict[str, Any]
    success_indicators: Dict[str, float]
    energy_impact: float
    convergence_contribution: Dict[str, float]
