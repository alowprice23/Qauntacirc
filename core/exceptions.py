# core/exceptions.py

"""
Defines custom exception types for the QuantaCirc core system.

Using custom exceptions allows for more specific error handling and provides
a clear hierarchy of potential issues that can arise within the system.
"""

class QuantaCircError(Exception):
    """Base class for all exceptions in the QuantaCirc core system."""
    pass

# --- Configuration and Initialization Errors ---

class ConfigurationError(QuantaCircError):
    """Raised when there is an error in the system's configuration."""
    pass

class InitializationError(QuantaCircError):
    """Raised when a component fails to initialize correctly."""
    pass

# --- State and Validation Errors ---

class StateError(QuantaCircError):
    """Raised for errors related to the logical state of the system."""
    pass

class ValidationError(StateError):
    """
    Raised when a data structure or state fails a validation check.
    This is a more specific version of StateError.
    """
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"{super().__str__()} | Details: {self.details}"
        return super().__str__()

# --- Calculation and Computation Errors ---

class CalculationError(QuantaCircError):
    """Raised during a numerical or metric calculation failure."""
    pass

class EnergyCalculationError(CalculationError):
    """Raised specifically during the calculation of system energy."""
    pass

# --- Optimization and Process Errors ---

class OptimizationError(QuantaCircError):
    """Raised for errors occurring during the optimization process (e.g., annealing)."""
    pass

class ConvergenceError(OptimizationError):
    """Raised if the system fails to converge or diverges."""
    pass

class BudgetError(QuantaCircError):
    """Raised for issues related to the error budget."""
    pass


# --- Messaging Errors ---

class MessagingError(QuantaCircError):
    """Raised for general errors within the messaging subsystem."""
    pass

class QuantumStateError(ValidationError):
    """
    Raised for errors related to quantum state validation or consistency.
    Inherits from ValidationError to support detailed error reporting.
    """
    pass

class SchemaValidationError(ValidationError):
    """
    Raised when a message payload does not conform to its schema.
    Inherits from ValidationError to support detailed error reporting.
    """
    pass


# Example of how these might be used:

def example_function(value):
    if not isinstance(value, int):
        raise ConfigurationError(f"Expected an integer, but got {type(value).__name__}")
    if value < 0:
        raise ValidationError("Value cannot be negative.", {"value": value})
    if value > 100:
        raise OptimizationError("Value exceeds optimization bounds.")

if __name__ == '__main__':
    print("--- Demonstrating custom exceptions ---")

    try:
        example_function("not-an-int")
    except QuantaCircError as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")

    try:
        example_function(-5)
    except QuantaCircError as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")
        # Showcasing the details attribute
        if isinstance(e, ValidationError):
            print(f"Validation details: {e.details}")

    try:
        example_function(200)
    except QuantaCircError as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")

    print("\n--- Exception Hierarchy ---")
    # A ValidationError is also a StateError and a QuantaCircError
    err = ValidationError("test", {})
    print(f"Is ValidationError a StateError? {isinstance(err, StateError)}")
    print(f"Is ValidationError a QuantaCircError? {isinstance(err, QuantaCircError)}")
    print(f"Is StateError a CalculationError? {isinstance(StateError('t'), CalculationError)}")
