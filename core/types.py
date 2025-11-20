# core/types.py

"""
Core System Types & Data Architecture for QuantaCirc.

This module defines the complete data architecture that all components will use.
It establishes the data contracts for communication, state representation,
and results across the entire system.
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4
<<<<<<< HEAD
<<<<<<< HEAD
from enum import Enum
=======
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure

from pydantic import BaseModel, Field, field_validator, model_validator

# ==============================================================================
# Core State Representation
# ==============================================================================

class EnergyComponents(BaseModel):
    """Energy function decomposition."""
    static: float = Field(..., description="Static component of the energy.")
    dynamic: float = Field(..., description="Dynamic component of the energy.")
    interaction: float = Field(..., description="Interaction component of the energy.")

    @property
    def total(self) -> float:
        """Computed total energy."""
        return self.static + self.dynamic + self.interaction

class SoftwareState(BaseModel):
    """Represents the state of various software components."""
    component_versions: Dict[str, str] = Field(..., description="Version numbers of software components.")
    config_hashes: Dict[str, str] = Field(..., description="Configuration file hashes.")
    status: str = Field("nominal", description="Overall software system status.")

class QuantumState(BaseModel):
    """Represents the quantum state of the system."""
    state_vector: List[complex] = Field(..., description="The state vector representing the quantum state.")
    density_matrix: Optional[List[List[complex]]] = Field(None, description="The density matrix, if applicable.")
    measurement_basis: str = Field("computational", description="The basis for measurement.")

class QCState(BaseModel):
    """Core software system state representation."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the state snapshot.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the state snapshot.")
    software_state: SoftwareState = Field(..., description="State of the classical software components.")
    quantum_state: Optional[QuantumState] = Field(None, description="State of the quantum system, if applicable.")
    energy: float = Field(..., description="Total system energy.")
    energy_components: EnergyComponents = Field(..., description="Breakdown of system energy components.")
    lyapunov_potential: float = Field(..., description="Lyapunov potential of the current state.")
    contraction_factor: float = Field(..., description="Contraction factor for the system's state space map.")
    optimization_phase: str = Field("initialization", description="Current phase of the optimization process.")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata for the state.")

    @model_validator(mode='after')
    def check_energy_components(self) -> 'QCState':
        """Validates that the total energy matches the sum of its components."""
        if self.energy_components and not abs(self.energy - self.energy_components.total) < 1e-9:
            raise ValueError("Total energy must equal the sum of its components.")
        return self

    @field_validator('contraction_factor')
    def contraction_factor_must_be_valid(cls, v: float) -> float:
        """Validates that the contraction factor is between 0 and 1."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("Contraction factor must be between 0 and 1.")
        return v

# ==============================================================================
# Agent Communication Protocol
# ==============================================================================

<<<<<<< HEAD
<<<<<<< HEAD
class Status(str, Enum):
    """Status of an agent operation."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

=======
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
class AgentTask(BaseModel):
    """Communication protocol for agent requests."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the task.")
    agent_name: str = Field(..., description="Name of the target agent.")
    task_type: str = Field(..., description="Type of task to be performed.")
    payload: Dict[str, Any] = Field(..., description="Task-specific data payload.")
    priority: int = Field(5, ge=1, le=10, description="Task priority (1-10).")
<<<<<<< HEAD
<<<<<<< HEAD
    status: Status = Field(Status.SUCCESS, description="Status of the proposal.")
    reason: Optional[str] = Field(None, description="Reason for failure, if any.")
=======
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
    quantum_context: Optional[QCState] = Field(None, description="The QCState context for the task.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of task creation.")

class AgentResult(BaseModel):
    """Communication protocol for agent responses."""
    task_id: UUID = Field(..., description="Identifier of the task this is a result for.")
    agent_name: str = Field(..., description="Name of the agent that performed the task.")
    action_taken: bool = Field(..., description="Indicates if the agent took a substantive action.")
<<<<<<< HEAD
<<<<<<< HEAD
    status: Status = Field(Status.SUCCESS, description="Status of the action.")
    result: Optional[Dict[str, Any]] = Field(None, description="The result of the action.")
=======
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
    energy_delta: Optional[Dict[str, float]] = Field(None, description="Change in energy components due to the action.")
    error: Optional[str] = Field(None, description="Error message, if any.")
    artifacts: List[str] = Field([], description="List of URIs to any generated artifacts (e.g., plots, logs).")
    verification_required: bool = Field(False, description="Whether this result requires formal verification.")

# ==============================================================================
# Mathematical & Verification Types
# ==============================================================================

class LyapunovResult(BaseModel):
    """Result of a Lyapunov stability analysis."""
    exponent: float = Field(..., description="Calculated Lyapunov exponent.")
    convergence_status: str = Field(..., description="Status of the convergence test.")
    iterations: int = Field(..., description="Number of iterations performed.")

class StateTransformation(BaseModel):
    """Represents a transformation from one state to another."""
    source_state_id: UUID = Field(..., description="ID of the source state.")
    target_state_id: UUID = Field(..., description="ID of the target state.")
    transform_matrix: List[List[float]] = Field(..., description="Matrix representing the transformation.")
    description: str = Field(..., description="Description of the transformation.")

class ConstraintViolation(BaseModel):
    """Details of a violated constraint."""
    constraint_name: str = Field(..., description="Name of the violated constraint.")
    violation_details: Dict[str, Any] = Field(..., description="Details of the violation.")

class SMTResult(BaseModel):
    """Result from an SMT solver."""
    satisfiable: bool = Field(..., description="Whether the formula is satisfiable.")
    model: Optional[Dict[str, Any]] = Field(None, description="A model for the formula, if satisfiable.")

class ProofCertificate(BaseModel):
    """A formal proof certificate."""
    proof_id: UUID = Field(default_factory=uuid4, description="Unique ID for the proof.")
    content: str = Field(..., description="The content of the proof (e.g., in a formal language).")
    verifier: str = Field(..., description="Name of the verifier or theorem prover used.")
    assumptions: List[str] = Field([], description="Assumptions made in the proof.")

# ==============================================================================
# System Operation & Reporting
# ==============================================================================

class RunRecord(BaseModel):
    """Record of a complete system run."""
    run_id: UUID = Field(default_factory=uuid4, description="Unique ID for the run.")
    start_time: datetime = Field(..., description="Start time of the run.")
    end_time: datetime = Field(..., description="End time of the run.")
    status: str = Field(..., description="Final status of the run (e.g., 'completed', 'failed').")
    initial_state: QCState = Field(..., description="The initial state of the system.")
    final_state: QCState = Field(..., description="The final state of the system.")
    results: List[AgentResult] = Field([], description="List of all agent results from the run.")

    @model_validator(mode='after')
    def check_times(self) -> 'RunRecord':
        """Ensures that end_time is not before start_time."""
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError("end_time must not be before start_time")
        return self

class VerificationReport(BaseModel):
    """Report from a verification task."""
    report_id: UUID = Field(default_factory=uuid4, description="Unique ID for the report.")
    verified_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of verification.")
    is_valid: bool = Field(..., description="Overall validity judgment.")
    details: Dict[str, Union[SMTResult, ProofCertificate, str]] = Field(..., description="Detailed results from verification components.")

    def to_json_schema(self):
        return self.schema_json(indent=2)
<<<<<<< HEAD
<<<<<<< HEAD

# ==============================================================================
# CLI Application Context
# ==============================================================================
from rich.console import Console

class ProjectConfig(BaseModel):
    pass

class AgentConfig(BaseModel):
    pass

class ExecutionConfig(BaseModel):
    pass

class MemoryConfig(BaseModel):
    pass

class SecurityConfig(BaseModel):
    pass

class QuantaCircConfig(BaseModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    agents: AgentConfig = Field(default_factory=AgentConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

class AppContext(BaseModel):
    config: QuantaCircConfig
    console: Console
    interactive: bool
    log_level: str

    class Config:
        arbitrary_types_allowed = True

    def verify_quantum_state(self) -> bool:
        # Dummy implementation
        return True
=======
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
