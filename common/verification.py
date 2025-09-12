from dataclasses import dataclass

@dataclass
class ConservationProof:
    energy_before: float
    energy_after: float
    conservation_error: float  # Must be < tolerance
    mathematical_justification: str

@dataclass
class ConvergenceProof:
    lyapunov_before: float
    lyapunov_after: float
    descent_amount: float  # Must be > 0 or within excursion bounds
    convergence_rate: float  # λ factor for Phase B

@dataclass
class StabilityProof:
    description: str
    is_stable: bool
    details: str # e.g., Lyapunov stability criteria check

@dataclass
class PerformanceGuarantee:
    description: str
    bound: str # e.g., "O(n log n)"
    verified: bool

@dataclass
class AgentCertificate:
    agent_id: str
    physics_principle: str
    mathematical_formula: str
    conservation_proof: ConservationProof
    convergence_proof: ConvergenceProof
    stability_proof: StabilityProof
    performance_guarantee: PerformanceGuarantee
