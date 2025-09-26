# core/__init__.py

"""
QuantaCirc Core System
======================

This package contains the core components of the QuantaCirc system, including
the computational engine, state representation, and optimization algorithms.
"""

# --- Core Components ---
from .energy_calculator import EnergyCalculator
from .lyapunov_monitor import LyapunovMonitor
from .two_phase_annealer import TwoPhaseAnnealer
from .functor import Functor
from .orchestrator import Orchestrator
from .convergence_engine import ConvergenceEngine
from .state_space import StateSpace

# --- Data Management and Validation ---
from .run_ledger import RunLedger
from .persistence import PersistenceManager
from .constraint_solver import SMTConstraintSolver
from .closure_rules import ClosureRuleSet
from .validators import validate_qc_state_consistency
from .serialization import serialize_model, deserialize_model, save_model_to_json, load_model_from_json

# --- Metrics and Utilities ---
from .metrics import collect_all_metrics
from .edit_distance import software_state_edit_distance, qcstate_edit_distance
from .error_budget import ErrorBudget

# --- Core Data Types ---
from .types import (
    QCState,
    EnergyComponents,
    SoftwareState,
    QuantumState,
    RunRecord,
    AgentTask,
    AgentResult,
    LyapunovResult,
    ConstraintViolation,
    SMTResult,
    ProofCertificate
)

# --- Custom Exceptions ---
from .exceptions import (
    QuantaCircError,
    ConfigurationError,
    InitializationError,
    StateError,
    ValidationError,
    CalculationError,
    EnergyCalculationError,
    OptimizationError,
    ConvergenceError,
    BudgetError
)


# Define the public API of the 'core' module
__all__ = [
    # Core Components
    "Orchestrator",
    "EnergyCalculator",
    "Functor",
    "LyapunovMonitor",
    "TwoPhaseAnnealer",
    "ConvergenceEngine",
    "StateSpace",

    # Data Management
    "RunLedger",
    "PersistenceManager",
    "SMTConstraintSolver",
    "ClosureRuleSet",
    "validate_qc_state_consistency",
    "serialize_model",
    "deserialize_model",
    "save_model_to_json",
    "load_model_from_json",

    # Metrics & Utilities
    "collect_all_metrics",
    "software_state_edit_distance",
    "qcstate_edit_distance",
    "ErrorBudget",

    # Core Data Types
    "QCState",
    "EnergyComponents", # Exported instead of QCEnergy
    "SoftwareState",
    "QuantumState",
    "RunRecord",
    "AgentTask",
    "AgentResult",
    "LyapunovResult",
    "ConstraintViolation",
    "SMTResult",
    "ProofCertificate",

    # Custom Exceptions
    "QuantaCircError",
    "ConfigurationError",
    "InitializationError",
    "StateError",
    "ValidationError",
    "CalculationError",
    "EnergyCalculationError",
    "OptimizationError",
    "ConvergenceError",
    "BudgetError",
]
