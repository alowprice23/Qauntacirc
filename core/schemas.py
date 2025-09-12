"""
This file contains the detailed, physics-based Pydantic schemas for the
core data structures of the QuantaCirc system, such as Intent and Plan.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional, Set
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# --- Supporting Enums and Simple Models ---

class Priority(str, Enum):
    """Urgency classification with queueing theory optimization."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EffortLevel(str, Enum):
    """Complexity assessment with information theory."""
    TRIVIAL = "TRIVIAL"
    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"

class CNLValidation(BaseModel):
    """Validation result for Controlled Natural Language translation."""
    status: str
    confidence: float
    reason: Optional[str] = None

# --- Mathematical and Physics-Based Primitives ---

class EnergyEstimate(BaseModel):
    """Predicted E_approx impact."""
    e_complexity: float = Field(..., description="Energy from complexity (K_approx + H)")
    e_coupling: float = Field(..., description="Energy from module coupling (Tr(L))")
    e_constraint: float = Field(..., description="Energy from constraint violations")
    e_debt: float = Field(..., description="Energy from technical debt")

    def total(self) -> float:
        return self.e_complexity + self.e_coupling + self.e_constraint + self.e_debt

class RiskBound(BaseModel):
    """Statistical risk with Chernoff bounds."""
    risk_level: float
    confidence: float
    method: str = "Chernoff"

class QuantumSignatures(BaseModel):
    """Mathematical fingerprints of the intent."""
    semantic_hash: str
    complexity_spectrum: List[float]

class IntentContext(BaseModel):
    """Mathematical context with energy state."""
    session_id: str
    prior_state_hash: Optional[str] = None
    current_energy: float

# --- Core Intent Schema ---

class Intent(BaseModel):
    """
    The structured representation of a user's request, with mathematical
    and physics-based constraints.
    """
    goal: str = Field(..., description="Primary objective with CNL validation")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Formal constraints with logical consistency")
    context: IntentContext = Field(..., description="Mathematical context with energy state")
    priority: Priority = Field(default=Priority.MEDIUM, description="Urgency classification with queueing theory optimization")
    acceptance_criteria: List[str] = Field(..., description="Success conditions with measurable predicates")
    energy_estimate: EnergyEstimate = Field(..., description="Predicted E_approx impact")
    risk_assessment: RiskBound = Field(..., description="Statistical risk with Chernoff bounds")
    requires_approval: bool = Field(default=False, description="Human-in-the-loop flag with risk thresholds")
    estimated_effort: EffortLevel = Field(default=EffortLevel.MODERATE, description="Complexity assessment with information theory")
    quantum_signatures: QuantumSignatures = Field(..., description="Mathematical fingerprints")

# --- Core Plan Schemas ---

class PlanNode(BaseModel):
    """An execution node in a plan, representing a quantum state."""
    id: str
    description: str
    agent_name: str
    task_payload: Dict[str, Any]
    energy_barrier: float = Field(..., description="Energy barrier to start this task")

class PlanEdge(BaseModel):
    """A dependency between plan nodes with transition probabilities."""
    from_node: str
    to_node: str
    transition_probability: float
    description: str

class VerificationPoint(BaseModel):
    """A mathematical checkpoint in the plan."""
    node_id: str
    proof_obligation: str
    verification_method: str = "SMT"

class EnergyMetrics(BaseModel):
    """Predicted quantum state changes from a plan."""
    delta_energy: float
    delta_entropy: float

class ConvergenceProof(BaseModel):
    """Mathematical guarantee of plan termination."""
    method: str = "Banach Fixed-Point"
    proof_certificate: str

class LyapunovCertificate(BaseModel):
    """Stability proof for the plan."""
    function_definition: str
    descent_guarantee: bool

class PlanMetadata(BaseModel):
    """Resource requirements and risk assessments for a plan."""
    required_capabilities: Set[str]
    estimated_duration_seconds: float
    risk_mitigations: List[str]

class Plan(BaseModel):
    """
    An executable plan as a quantum state evolution, represented as a
    directed acyclic graph (DAG) of tasks.
    """
    id: str = Field(default_factory=lambda: f"plan-{uuid4()}", description="Unique plan identifier with cryptographic hash")
    intent: Intent = Field(..., description="Source intent with full traceability")
    nodes: List[PlanNode] = Field(..., description="Execution nodes as quantum states")
    edges: List[PlanEdge] = Field(..., description="Dependencies with transition probabilities")
    metadata: PlanMetadata = Field(..., description="Resource requirements and risk assessments")
    verification_points: List[VerificationPoint] = Field(..., description="Mathematical checkpoints")
    energy_impact: EnergyMetrics = Field(..., description="Predicted quantum state changes")
    convergence_proof: ConvergenceProof = Field(..., description="Mathematical guarantee of termination")
    lyapunov_certificate: LyapunovCertificate = Field(..., description="Stability proof")
