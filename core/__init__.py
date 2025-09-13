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
from .orchestrator import Orchestrator
from .closure_validator import ClosureValidator
from .agent_pool import AgentPool


# --- Core Data Types ---
from .data_models import (
    SystemState,
    EnergyBreakdown,
    LyapunovMetrics,
    Obligation,
    ClosureResult,
    Agent,
    AgentAction,
    ComposedAction,
    Module,
    DependencyGraph,
    Constraint,
    SystemEvolution,
    AnnealingResult,
    ContractionResult,
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
    "LyapunovMonitor",
    "TwoPhaseAnnealer",
    "ClosureValidator",
    "AgentPool",

    # Core Data Types
    "SystemState",
    "EnergyBreakdown",
    "LyapunovMetrics",
    "Obligation",
    "ClosureResult",
    "Agent",
    "AgentAction",
    "ComposedAction",
    "Module",
    "DependencyGraph",
    "Constraint",
    "SystemEvolution",
    "AnnealingResult",
    "ContractionResult",

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
