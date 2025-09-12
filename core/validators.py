# core/validators.py

"""
Provides high-level data and state validators for the core system.

These functions go beyond the basic type validation provided by Pydantic
and check for logical consistency, semantic integrity, and adherence to
domain-specific business rules.
"""

from __future__ import annotations

from typing import List, Tuple

from core.types import QCState, RunRecord, SoftwareState

class ValidationError(Exception):
    """Custom exception for validation failures."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}

def validate_qc_state_consistency(state: QCState) -> None:
    """
    Performs a deep validation of a QCState for logical consistency.

    Args:
        state: The QCState object to validate.

    Raises:
        ValidationError: If any consistency checks fail.
    """
    # Pydantic's built-in validator already checks if energy components sum up.
    # We can add more complex, domain-specific rules here.

    # Example rule: In exploitation phase, lyapunov potential should be low.
    if state.phase == "exploitation" and state.lyapunov_metrics.phi > 1.0:
        # This threshold is arbitrary, for demonstration purposes.
        raise ValidationError(
            "High Lyapunov potential detected during exploitation phase.",
            {"lyapunov_potential": state.lyapunov_metrics.phi, "threshold": 1.0}
        )

    # Example rule: Quantum state should exist if not in initialization phase
    if state.phase != "initialization" and state.quantum_state is None:
        raise ValidationError(
            "Quantum state must be present after the initialization phase.",
            {"optimization_phase": state.phase}
        )

    # Check normalization of quantum state vector
    if state.quantum_state:
        import numpy as np
        norm = np.linalg.norm(state.quantum_state.state_vector)
        if not np.isclose(norm, 1.0):
            raise ValidationError(
                "Quantum state vector is not normalized.",
                {"norm": norm}
            )

def validate_run_record(record: RunRecord) -> None:
    """
    Validates a RunRecord for logical integrity.

    Args:
        record: The RunRecord object to validate.

    Raises:
        ValidationError: If the record is found to be inconsistent.
    """
    # Pydantic validator handles start_time < end_time.

    # Rule: For a 'completed' run, final energy should ideally be lower than initial.
    # This might not always be true due to annealing, but we can flag large increases.
    if record.status == "completed":
        if record.final_state.energy_breakdown.total > record.initial_state.energy_breakdown.total * 1.1: # Allow 10% increase
             raise ValidationError(
                "Final energy in completed run is significantly higher than initial energy.",
                {"initial_energy": record.initial_state.energy_breakdown.total, "final_energy": record.final_state.energy_breakdown.total}
            )

    # Rule: The final state's timestamp must be on or after the initial state's.
    if record.final_state.timestamp < record.initial_state.timestamp:
        raise ValidationError(
            "Final state timestamp cannot be before initial state timestamp.",
            {"initial_timestamp": record.initial_state.timestamp, "final_timestamp": record.final_state.timestamp}
        )

def validate_software_state(software_state: SoftwareState) -> None:
    """
    Validates a SoftwareState object for data integrity.

    Args:
        software_state: The SoftwareState to validate.

    Raises:
        ValidationError: If the state is missing required information.
    """
    # Rule: Component versions and config hashes should not have empty keys or values.
    for name, version in software_state.component_versions.items():
        if not name or not version:
            raise ValidationError(
                "Component versions contain empty names or values.",
                {"component": name, "version": version}
            )

    for name, a_hash in software_state.config_hashes.items():
        if not name or not a_hash:
            raise ValidationError(
                "Config hashes contain empty names or values.",
                {"config": name, "hash": a_hash}
            )

# Example Usage
if __name__ == '__main__':
    from uuid import uuid4
    from datetime import datetime
    from core.types import EnergyBreakdown, QuantumState, LyapunovMetrics, SoftwareState

    # --- Test QCState Validator ---
    print("--- Testing QCState Validator ---")

    eb = EnergyBreakdown(total=10, complexity=5, coupling=5, constraint=0, debt=0)
    lm = LyapunovMetrics(phi=0.5, energy=10, test_penalty=0, obligation_penalty=0)

    valid_state = QCState(
        id=uuid4(), timestamp=datetime.utcnow(),
        software_state=SoftwareState(component_versions={"a":"1"}, config_hashes={"b":"2"}),
        energy_breakdown=eb,
        lyapunov_metrics=lm,
        contraction_factor=0.8,
        phase="exploitation",
        quantum_state=QuantumState(state_vector=[1.0, 0.0])
    )
    try:
        validate_qc_state_consistency(valid_state)
        print("Valid QCState passed validation.")
    except ValidationError as e:
        print(f"Validation failed unexpectedly for valid state: {e}")

    invalid_lm = lm.model_copy(update={'phi': 2.0})
    invalid_state_lyapunov = valid_state.model_copy(update={'lyapunov_metrics': invalid_lm})
    try:
        validate_qc_state_consistency(invalid_state_lyapunov)
    except ValidationError as e:
        print(f"Caught expected error for high Lyapunov potential: {e}")

    invalid_state_norm = valid_state.model_copy(deep=True)
    invalid_state_norm.quantum_state.state_vector = [2.0, 0.0]
    try:
        validate_qc_state_consistency(invalid_state_norm)
    except ValidationError as e:
        print(f"Caught expected error for non-normalized state: {e}")

    # --- Test RunRecord Validator ---
    # ... (similar tests could be added for RunRecord and SoftwareState)
