from __future__ import annotations
from typing import Dict, Any, List, Optional, Literal
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import field_validator, model_validator, BaseModel, Field, validator
from enum import Enum

class EnergyComponents(BaseModel):
    static: float
    dynamic: float
    interaction: float

    @property
    def total(self) -> float:
        return self.static + self.dynamic + self.interaction

class SoftwareState(BaseModel):
    component_versions: Dict[str, str]
    config_hashes: Dict[str, str]
    status: str = "nominal"

class QuantumState(BaseModel):
    state_vector: List[complex]
    eigenvalues: Optional[List[float]] = None
    density_matrix: Optional[List[List[complex]]] = None

class QCState(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    software_state: SoftwareState
    quantum_state: Optional[QuantumState] = None
    energy: float
    energy_components: EnergyComponents
    lyapunov_potential: float
    contraction_factor: float
    failing_tests: int = 0
    open_obligations: int = 0
    optimization_phase: str = "initialization"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def energy_must_be_sum_of_components(cls, values):
        energy = values.get('energy')
        energy_components_data = values.get('energy_components')
        if energy is not None and energy_components_data is not None:
            if isinstance(energy_components_data, dict):
                energy_components = EnergyComponents(**energy_components_data)
                if not abs(energy - energy_components.total) < 1e-9:
                    raise ValueError('Total energy must equal the sum of its components.')
            elif isinstance(energy_components_data, EnergyComponents):
                if not abs(energy - energy_components_data.total) < 1e-9:
                    raise ValueError('Total energy must equal the sum of its components.')
        return values

    @field_validator('contraction_factor')
    @classmethod
    def contraction_factor_must_be_between_0_and_1(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError('Contraction factor must be between 0 and 1.')
        return v

class TaskQuanta(BaseModel):
    id: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    verification_criteria: List[str]
    spec_stub: Optional[str] = None
    energy: float = 0.0
    priority: int = Field(5, ge=1, le=10)

class Status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"

class AgentTask(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    agent_name: str
    task_type: str
    payload: Dict[str, Any] | List[TaskQuanta]
    priority: int = Field(5, ge=1, le=10)
    quantum_context: Optional[QCState] = None
    status: Status = Status.PENDING
    reason: Optional[str] = None

class AgentResult(BaseModel):
    task_id: UUID
    agent_name: str
    action_taken: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: Status = Status.PENDING

class RunRecord(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    start_time: datetime
    end_time: datetime
    status: Literal["completed", "failed", "running"]
    initial_state: QCState
    final_state: QCState
    actions: List[AgentResult] = Field(default_factory=list)

    @model_validator(mode='after')
    def end_time_must_be_after_start_time(self) -> "RunRecord":
        if self.end_time < self.start_time:
            raise ValueError('end_time must not be before start_time')
        return self

class LyapunovResult(BaseModel):
    is_stable: bool
    convergence_rate: Optional[float] = None
    convergence_status: Optional[str] = None
    exponent: Optional[float] = None
    iterations: Optional[int] = None


class ConstraintViolation(BaseModel):
    constraint_name: str
    details: str

class SMTResult(BaseModel):
    is_satisfiable: bool
    model: Optional[Dict[str, Any]] = None

class ProofCertificate(BaseModel):
    proof_id: UUID = Field(default_factory=uuid4)
    prover: str
    content: str

from typing import Any

class QuantaCircConfig(BaseModel):
    pass

class AppContext(BaseModel):
    config: QuantaCircConfig
    console: Any
    interactive: bool
    log_level: str

    def verify_quantum_state(self) -> bool:
        """
        Placeholder for verifying quantum state consistency.
        In a real implementation, this would check for things like
        trace(rho) = 1, rho is positive semi-definite, etc.
        """
        return True

    class Config:
        arbitrary_types_allowed = True


Proposal = AgentTask
State = QCState
Action = AgentResult
