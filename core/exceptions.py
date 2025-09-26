# core/exceptions.py
"""
Custom exceptions for the QuantaCirc system.
"""

class QuantaCircError(Exception):
    """Base exception for all errors in the QuantaCirc system."""
    def __init__(self, message, suggested_fix=None):
        self.message = message
        self.suggested_fix = suggested_fix
        super().__init__(self.message)

class ConfigurationError(QuantaCircError):
    """Error related to system configuration."""
    pass

class InitializationError(QuantaCircError):
    """Error during the initialization of a component."""
    pass

class StateError(QuantaCircError):
    """Error related to an invalid or inconsistent state."""
    pass

class ValidationError(QuantaCircError):
    """Error during data validation."""
    pass

class CalculationError(QuantaCircError):
    """Generic error during a calculation."""
    pass

class EnergyCalculationError(CalculationError):
    """Error specifically during energy calculation."""
    pass

class OptimizationError(QuantaCircError):
    """Error during the optimization process."""
    pass

class ConvergenceError(OptimizationError):
    """Error related to failure to converge."""
    pass

class BudgetError(QuantaCircError):
    """Error related to exhausted budgets (e.g., error budget)."""
    pass

class MessagingError(QuantaCircError):
    """Error related to the messaging system."""
    pass

class QuantumStateError(StateError):
    """Error related to an invalid quantum state."""
    pass

class VerificationError(QuantaCircError):
    """Base exception for verification failures."""
    pass

class ProofObligationError(VerificationError):
    """Error related to discharging a proof obligation."""
    def __init__(self, message, obligation, details=None, suggested_fix=None):
        self.obligation = obligation
        self.details = details or {}
        super().__init__(message, suggested_fix)

class SMTSolvingError(VerificationError):
    """Error during SMT solving."""
    pass
